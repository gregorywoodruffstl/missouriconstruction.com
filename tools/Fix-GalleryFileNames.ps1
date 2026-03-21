# ============================================================
# Fix-GalleryFileNames.ps1
#
# Pads single-digit months AND days in photo filenames so they
# sort correctly in chronological order.
#
# Example renames:
#   2004_1_17_001.jpg  ->  2004_01_17_001.jpg
#   2005_3_4_022.jpg   ->  2005_03_04_022.jpg
#
# Handles both underscore-separated (2004_1_17) and
# hyphen-separated (2004-1-17) date patterns.
#
# USAGE:
#   1. Right-click this script -> "Run with PowerShell"
#      OR in a terminal:
#         .\Fix-GalleryFileNames.ps1 -FolderPath "D:\BuschStadiumPhotos"
#
#   2. Dry run first (no changes made, just previewed):
#         .\Fix-GalleryFileNames.ps1 -FolderPath "D:\BuschStadiumPhotos" -DryRun
#
# ============================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$FolderPath = ".",

    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

# Resolve to absolute path
$FolderPath = (Resolve-Path $FolderPath).Path

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  GALLERY FILENAME ZERO-PADDER" -ForegroundColor Cyan
Write-Host "  Folder: $FolderPath" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "  MODE: DRY RUN (no files changed)" -ForegroundColor Yellow
} else {
    Write-Host "  MODE: LIVE RUN" -ForegroundColor Green
}
Write-Host "=" * 60 -ForegroundColor Cyan

$files = Get-ChildItem -Path $FolderPath -Recurse -File -Include "*.jpg","*.jpeg","*.png","*.gif","*.webp"

$renamed = 0
$skipped = 0

foreach ($file in $files) {
    $name = $file.Name
    $base = $file.BaseName
    $ext  = $file.Extension

    # Pattern 1: YYYY_M_D or YYYY_M_DD or YYYY_MM_D  (underscore separator)
    # Pattern 2: YYYY-M-D or YYYY-M-DD or YYYY-MM-D  (hyphen separator)
    # Captures year, separator, month, day, and any trailing suffix

    $newBase = $base

    # Underscore pattern: 2004_1_17... or 2004_01_3...
    if ($base -match '^(\d{4})_(\d{1,2})_(\d{1,2})(.*)$') {
        $year    = $Matches[1]
        $month   = $Matches[2].PadLeft(2, '0')
        $day     = $Matches[3].PadLeft(2, '0')
        $suffix  = $Matches[4]
        $newBase = "${year}_${month}_${day}${suffix}"
    }
    # Hyphen pattern: 2004-1-17... or 2004-01-3...
    elseif ($base -match '^(\d{4})-(\d{1,2})-(\d{1,2})(.*)$') {
        $year    = $Matches[1]
        $month   = $Matches[2].PadLeft(2, '0')
        $day     = $Matches[3].PadLeft(2, '0')
        $suffix  = $Matches[4]
        $newBase = "${year}-${month}-${day}${suffix}"
    }
    # Also handle folder-style: month folder is a single digit (rename folder names)
    # (handled separately below)

    $newName = "${newBase}${ext}"

    if ($newName -ne $name) {
        $newPath = Join-Path $file.DirectoryName $newName
        if ($DryRun) {
            Write-Host "  [WOULD RENAME] $name  ->  $newName" -ForegroundColor Yellow
        } else {
            Rename-Item -LiteralPath $file.FullName -NewName $newName
            Write-Host "  [RENAMED] $name  ->  $newName" -ForegroundColor Green
        }
        $renamed++
    } else {
        $skipped++
    }
}

Write-Host ""
Write-Host "-" * 60
Write-Host "  Files examined : $($files.Count)"
Write-Host "  Renamed        : $renamed" -ForegroundColor $(if ($renamed -gt 0) { "Green" } else { "Gray" })
Write-Host "  Already correct: $skipped"

# ── Also fix FOLDER names that are single-digit months ───────────────────────
Write-Host ""
Write-Host "Checking folder names..."

$folders = Get-ChildItem -Path $FolderPath -Recurse -Directory |
           Where-Object { $_.Name -match '^\d{1}$' }   # single digit folder

$folderRenamed = 0
foreach ($folder in $folders) {
    $paddedName = $folder.Name.PadLeft(2, '0')
    $newFolderPath = Join-Path $folder.Parent.FullName $paddedName
    if ($DryRun) {
        Write-Host "  [WOULD RENAME FOLDER] $($folder.FullName)  ->  $paddedName" -ForegroundColor Yellow
    } else {
        Rename-Item -LiteralPath $folder.FullName -NewName $paddedName
        Write-Host "  [RENAMED FOLDER] $($folder.Name)  ->  $paddedName" -ForegroundColor Green
    }
    $folderRenamed++
}

if ($folderRenamed -eq 0) {
    Write-Host "  No single-digit folder names found." -ForegroundColor Gray
}

Write-Host ""
Write-Host "=" * 60
if ($DryRun) {
    Write-Host "  DRY RUN complete. Run without -DryRun to apply changes." -ForegroundColor Yellow
} else {
    Write-Host "  Done. Total renamed: $($renamed + $folderRenamed)" -ForegroundColor Green
}
Write-Host "=" * 60
