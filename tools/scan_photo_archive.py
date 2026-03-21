"""
Photo Archive Scanner
=====================
Walks a folder of photos organized by year/month and builds a JSON inventory.
Uses folder structure for dates (no EXIF required).
Also extracts real EXIF data where available (digital camera shots).

Usage:
    python scan_photo_archive.py "C:\path\to\your\photos"

Output:
    photo_inventory.json  — full inventory
    photo_summary.txt     — quick readable summary
"""

import os
import sys
import json
import struct
from datetime import datetime
from pathlib import Path


# ── EXIF helpers (no third-party libs needed) ────────────────────────────────

def _get_exif_data(filepath):
    """Extract basic EXIF from JPEG without any external library."""
    result = {
        'exif_date': None,
        'camera_make': None,
        'camera_model': None,
        'gps_lat': None,
        'gps_lon': None,
        'has_gps': False,
    }
    try:
        with open(filepath, 'rb') as f:
            data = f.read(65536)  # read first 64KB — enough for EXIF header

        # Find EXIF marker (0xFFE1)
        pos = data.find(b'\xff\xe1')
        if pos == -1:
            return result

        # Parse EXIF header
        exif_data = data[pos + 4:]
        if exif_data[:4] not in (b'Exif', b'MM\x00*', b'II*\x00'):
            return result

        # Look for date string pattern (YYYY:MM:DD HH:MM:SS)
        import re
        date_pattern = re.compile(rb'(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2})')
        match = date_pattern.search(exif_data)
        if match:
            try:
                raw = match.group(1).decode('ascii')
                dt = datetime.strptime(raw, '%Y:%m:%d %H:%M:%S')
                result['exif_date'] = dt.isoformat()
            except Exception:
                pass

        # Check for GPS IFD marker (rough check)
        if b'GPS' in exif_data or b'\x00\x02\x00\x00\x00' in exif_data:
            result['has_gps'] = True

    except Exception:
        pass
    return result


def _infer_date_from_path(filepath):
    """
    Try to extract year and month from folder path.
    Handles patterns like:
      .../2003/06/img.jpg
      .../2003-06/img.jpg
      .../2003/June/img.jpg
      .../Photos 2003/06/img.jpg
    """
    import re
    parts = Path(filepath).parts

    year = None
    month = None

    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    }

    for part in parts:
        # Look for 4-digit year (1970-2030)
        year_match = re.search(r'\b(19[7-9]\d|20[0-2]\d)\b', part)
        if year_match and not year:
            year = int(year_match.group(1))

        # Look for 2-digit month (01-12)
        month_match = re.fullmatch(r'0?([1-9]|1[0-2])', part)
        if month_match and not month:
            month = int(month_match.group(1))

        # Look for month name
        lower = part.lower().strip()
        if lower in month_names and not month:
            month = month_names[lower]

        # Look for YYYY-MM pattern in folder name
        ym_match = re.search(r'(19[7-9]\d|20[0-2]\d)[-_](\d{1,2})', part)
        if ym_match:
            year = int(ym_match.group(1))
            month = int(ym_match.group(2))

    return year, month


# ── Main scan ────────────────────────────────────────────────────────────────

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif', '.heic', '.webp'}


def scan_archive(root_folder):
    root = Path(root_folder)
    if not root.exists():
        print(f"ERROR: Folder not found: {root_folder}")
        sys.exit(1)

    print(f"\nScanning: {root}")
    print("This may take a moment for large archives...\n")

    inventory = []
    stats = {
        'total_images': 0,
        'with_real_exif_date': 0,
        'with_folder_date': 0,
        'with_gps': 0,
        'no_date': 0,
        'by_year': {},
    }

    all_files = list(root.rglob('*'))
    image_files = [f for f in all_files if f.suffix.lower() in IMAGE_EXTENSIONS and f.is_file()]
    total = len(image_files)
    print(f"Found {total:,} image files. Building inventory...")

    for i, filepath in enumerate(image_files):
        if i % 500 == 0 and i > 0:
            print(f"  Processed {i:,} / {total:,}...")

        rel_path = str(filepath.relative_to(root))
        file_stat = filepath.stat()
        file_size_kb = round(file_stat.st_size / 1024, 1)

        # Get EXIF data
        exif = _get_exif_data(filepath) if filepath.suffix.lower() in {'.jpg', '.jpeg', '.tif', '.tiff'} else {
            'exif_date': None, 'camera_make': None, 'camera_model': None,
            'gps_lat': None, 'gps_lon': None, 'has_gps': False
        }

        # Get date from folder path
        folder_year, folder_month = _infer_date_from_path(filepath)

        # Determine best date
        date_source = 'none'
        final_year = None
        final_month = None

        if exif['exif_date']:
            dt = datetime.fromisoformat(exif['exif_date'])
            final_year = dt.year
            final_month = dt.month
            date_source = 'exif'
            stats['with_real_exif_date'] += 1
        elif folder_year:
            final_year = folder_year
            final_month = folder_month
            date_source = 'folder'
            stats['with_folder_date'] += 1
        else:
            stats['no_date'] += 1

        if exif['has_gps']:
            stats['with_gps'] += 1

        if final_year:
            year_key = str(final_year)
            stats['by_year'][year_key] = stats['by_year'].get(year_key, 0) + 1

        record = {
            'path': rel_path,
            'filename': filepath.name,
            'size_kb': file_size_kb,
            'year': final_year,
            'month': final_month,
            'date_source': date_source,
            'exif_date': exif['exif_date'],
            'has_gps': exif['has_gps'],
            'folder_parts': [p for p in filepath.parent.relative_to(root).parts],
        }
        inventory.append(record)
        stats['total_images'] += 1

    return inventory, stats


def write_outputs(inventory, stats, output_dir):
    output_dir = Path(output_dir)

    # JSON inventory
    json_path = output_dir / 'photo_inventory.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'stats': stats,
            'photos': inventory,
        }, f, indent=2)
    print(f"\nInventory saved: {json_path}")
    print(f"File size: {json_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Readable summary
    summary_path = output_dir / 'photo_summary.txt'
    lines = [
        'PHOTO ARCHIVE INVENTORY SUMMARY',
        f'Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p")}',
        '=' * 50,
        f'Total images found:      {stats["total_images"]:,}',
        f'With real EXIF date:     {stats["with_real_exif_date"]:,}',
        f'Date from folder name:   {stats["with_folder_date"]:,}',
        f'No date found:           {stats["no_date"]:,}',
        f'Photos with GPS data:    {stats["with_gps"]:,}',
        '',
        'BY YEAR:',
        '-' * 30,
    ]

    for year in sorted(stats['by_year'].keys()):
        count = stats['by_year'][year]
        bar = '█' * min(count // 10, 50)
        lines.append(f'  {year}: {count:>5,}  {bar}')

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Summary saved:    {summary_path}")

    # Print summary to console too
    print('\n' + '\n'.join(lines))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scan_photo_archive.py \"C:\\path\\to\\your\\photos\"")
        print("\nExample:")
        print('  python scan_photo_archive.py "C:\\Users\\Woody\\Pictures"')
        print('  python scan_photo_archive.py "D:\\My Photos"')
        sys.exit(1)

    photo_root = sys.argv[1]

    # Output goes in same location as this script
    script_dir = Path(__file__).parent
    output_dir = script_dir

    inventory, stats = scan_archive(photo_root)
    write_outputs(inventory, stats, output_dir)

    print(f"\nDone! {stats['total_images']:,} images inventoried.")
    print("Copy photo_inventory.json and photo_summary.txt to your new laptop.")
