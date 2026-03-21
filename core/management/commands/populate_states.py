"""
Management command to populate US State data
Includes state flowers, trees, birds, mottos for header display

Usage:
    python manage.py populate_states
    python manage.py populate_states --dry-run
"""

from django.core.management.base import BaseCommand
from core.models import State


class Command(BaseCommand):
    help = 'Populate US States with flowers, trees, and symbols for display'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without saving'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # State data with flowers, trees, etc.
        # Focused on states with Springfields first!
        states_data = [
            {
                'name': 'Illinois',
                'abbreviation': 'IL',
                'capital': 'Springfield',  # The state capital IS Springfield!
                'state_flower': 'Violet',
                'state_tree': 'White Oak',
                'state_bird': 'Northern Cardinal',
                'state_motto': 'State Sovereignty, National Union',
                'region': 'Midwest'
            },
            {
                'name': 'Missouri',
                'abbreviation': 'MO',
                'capital': 'Jefferson City',
                'state_flower': 'White Hawthorn Blossom',
                'state_tree': 'Flowering Dogwood',
                'state_bird': 'Eastern Bluebird',
                'state_motto': 'Salus populi suprema lex esto (The welfare of the people shall be the supreme law)',
                'region': 'Midwest'
            },
            {
                'name': 'Massachusetts',
                'abbreviation': 'MA',
                'capital': 'Boston',
                'state_flower': 'Mayflower',
                'state_tree': 'American Elm',
                'state_bird': 'Black-capped Chickadee',
                'state_motto': 'Ense petit placidam sub libertate quietem (By the sword we seek peace, but peace only under liberty)',
                'region': 'Northeast'
            },
            {
                'name': 'Ohio',
                'abbreviation': 'OH',
                'capital': 'Columbus',
                'state_flower': 'Red Carnation',
                'state_tree': 'Ohio Buckeye',
                'state_bird': 'Northern Cardinal',
                'state_motto': 'With God, all things are possible',
                'region': 'Midwest'
            },
            {
                'name': 'Oregon',
                'abbreviation': 'OR',
                'capital': 'Salem',
                'state_flower': 'Oregon Grape',
                'state_tree': 'Douglas Fir',
                'state_bird': 'Western Meadowlark',
                'state_motto': 'Alis volat propriis (She flies with her own wings)',
                'region': 'West'
            },
            {
                'name': 'Pennsylvania',
                'abbreviation': 'PA',
                'capital': 'Harrisburg',
                'state_flower': 'Mountain Laurel',
                'state_tree': 'Eastern Hemlock',
                'state_bird': 'Ruffed Grouse',
                'state_motto': 'Virtue, Liberty, and Independence',
                'region': 'Northeast'
            },
            {
                'name': 'Tennessee',
                'abbreviation': 'TN',
                'capital': 'Nashville',
                'state_flower': 'Iris',
                'state_tree': 'Tulip Poplar',
                'state_bird': 'Northern Mockingbird',
                'state_motto': 'Agriculture and Commerce',
                'region': 'South'
            },
            {
                'name': 'Vermont',
                'abbreviation': 'VT',
                'capital': 'Montpelier',
                'state_flower': 'Red Clover',
                'state_tree': 'Sugar Maple',
                'state_bird': 'Hermit Thrush',
                'state_motto': 'Freedom and Unity',
                'region': 'Northeast'
            },
            {
                'name': 'Virginia',
                'abbreviation': 'VA',
                'capital': 'Richmond',
                'state_flower': 'American Dogwood',
                'state_tree': 'American Dogwood',
                'state_bird': 'Northern Cardinal',
                'state_motto': 'Sic semper tyrannis (Thus always to tyrants)',
                'region': 'South'
            },
            {
                'name': 'Wisconsin',
                'abbreviation': 'WI',
                'capital': 'Madison',
                'state_flower': 'Wood Violet',
                'state_tree': 'Sugar Maple',
                'state_bird': 'American Robin',
                'state_motto': 'Forward',
                'region': 'Midwest'
            },
            {
                'name': 'Colorado',
                'abbreviation': 'CO',
                'capital': 'Denver',
                'state_flower': 'Rocky Mountain Columbine',
                'state_tree': 'Colorado Blue Spruce',
                'state_bird': 'Lark Bunting',
                'state_motto': 'Nil sine numine (Nothing without Providence)',
                'region': 'West'
            },
            {
                'name': 'Georgia',
                'abbreviation': 'GA',
                'capital': 'Atlanta',
                'state_flower': 'Cherokee Rose',
                'state_tree': 'Live Oak',
                'state_bird': 'Brown Thrasher',
                'state_motto': 'Wisdom, Justice, and Moderation',
                'region': 'South'
            },
            {
                'name': 'Kentucky',
                'abbreviation': 'KY',
                'capital': 'Frankfort',
                'state_flower': 'Goldenrod',
                'state_tree': 'Tulip Poplar',
                'state_bird': 'Northern Cardinal',
                'state_motto': 'United we stand, divided we fall',
                'region': 'South'
            },
            {
                'name': 'Louisiana',
                'abbreviation': 'LA',
                'capital': 'Baton Rouge',
                'state_flower': 'Magnolia',
                'state_tree': 'Bald Cypress',
                'state_bird': 'Brown Pelican',
                'state_motto': 'Union, Justice, and Confidence',
                'region': 'South'
            },
            {
                'name': 'Michigan',
                'abbreviation': 'MI',
                'capital': 'Lansing',
                'state_flower': 'Apple Blossom',
                'state_tree': 'White Pine',
                'state_bird': 'American Robin',
                'state_motto': 'Si quaeris peninsulam amoenam circumspice (If you seek a pleasant peninsula, look about you)',
                'region': 'Midwest'
            },
            {
                'name': 'Minnesota',
                'abbreviation': 'MN',
                'capital': 'Saint Paul',
                'state_flower': 'Pink and White Lady\'s Slipper',
                'state_tree': 'Red Pine',
                'state_bird': 'Common Loon',
                'state_motto': 'L\'Étoile du Nord (The Star of the North)',
                'region': 'Midwest'
            },
            {
                'name': 'Nebraska',
                'abbreviation': 'NE',
                'capital': 'Lincoln',
                'state_flower': 'Goldenrod',
                'state_tree': 'Cottonwood',
                'state_bird': 'Western Meadowlark',
                'state_motto': 'Equality before the law',
                'region': 'Midwest'
            },
            {
                'name': 'New Hampshire',
                'abbreviation': 'NH',
                'capital': 'Concord',
                'state_flower': 'Purple Lilac',
                'state_tree': 'White Birch',
                'state_bird': 'Purple Finch',
                'state_motto': 'Live Free or Die',
                'region': 'Northeast'
            },
            {
                'name': 'New Jersey',
                'abbreviation': 'NJ',
                'capital': 'Trenton',
                'state_flower': 'Common Blue Violet',
                'state_tree': 'Northern Red Oak',
                'state_bird': 'Eastern Goldfinch',
                'state_motto': 'Liberty and Prosperity',
                'region': 'Northeast'
            },
            {
                'name': 'New York',
                'abbreviation': 'NY',
                'capital': 'Albany',
                'state_flower': 'Rose',
                'state_tree': 'Sugar Maple',
                'state_bird': 'Eastern Bluebird',
                'state_motto': 'Excelsior (Ever upward)',
                'region': 'Northeast'
            },
            {
                'name': 'South Carolina',
                'abbreviation': 'SC',
                'capital': 'Columbia',
                'state_flower': 'Yellow Jessamine',
                'state_tree': 'Palmetto',
                'state_bird': 'Carolina Wren',
                'state_motto': 'Dum spiro spero (While I breathe, I hope)',
                'region': 'South'
            },
            {
                'name': 'South Dakota',
                'abbreviation': 'SD',
                'capital': 'Pierre',
                'state_flower': 'Pasque Flower',
                'state_tree': 'Black Hills Spruce',
                'state_bird': 'Ring-necked Pheasant',
                'state_motto': 'Under God the people rule',
                'region': 'Midwest'
            },
            {
                'name': 'West Virginia',
                'abbreviation': 'WV',
                'capital': 'Charleston',
                'state_flower': 'Rhododendron',
                'state_tree': 'Sugar Maple',
                'state_bird': 'Northern Cardinal',
                'state_motto': 'Montani semper liberi (Mountaineers are always free)',
                'region': 'South'
            },
            {
                'name': 'Florida',
                'abbreviation': 'FL',
                'capital': 'Tallahassee',
                'state_flower': 'Orange Blossom',
                'state_tree': 'Sabal Palm',
                'state_bird': 'Northern Mockingbird',
                'state_motto': 'In God We Trust',
                'region': 'South'
            },
            {
                'name': 'Idaho',
                'abbreviation': 'ID',
                'capital': 'Boise',
                'state_flower': 'Syringa',
                'state_tree': 'Western White Pine',
                'state_bird': 'Mountain Bluebird',
                'state_motto': 'Esto perpetua (Let it be perpetual)',
                'region': 'West'
            },
            {
                'name': 'Arkansas',
                'abbreviation': 'AR',
                'capital': 'Little Rock',
                'state_flower': 'Apple Blossom',
                'state_tree': 'Loblolly Pine',
                'state_bird': 'Northern Mockingbird',
                'state_motto': 'Regnat populus (The people rule)',
                'region': 'South'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("POPULATING US STATES WITH SYMBOLS"))
        self.stdout.write("="*70 + "\n")
        
        for state_data in states_data:
            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would create/update: {state_data['name']} ({state_data['abbreviation']})"
                )
                self.stdout.write(f"  Flower: {state_data['state_flower']}")
                self.stdout.write(f"  Tree: {state_data['state_tree']}")
                self.stdout.write(f"  Bird: {state_data['state_bird']}")
                self.stdout.write("")
                continue
            
            # Create or update state
            state, created = State.objects.update_or_create(
                abbreviation=state_data['abbreviation'],
                defaults=state_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created: {state.name} ({state.abbreviation})")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"↻ Updated: {state.name} ({state.abbreviation})")
                )
            
            self.stdout.write(f"  Flower: {state.state_flower}")
            self.stdout.write(f"  Tree: {state.state_tree}")
            self.stdout.write("")
        
        # Summary
        self.stdout.write("\n" + "="*70)
        if dry_run:
            self.stdout.write(self.style.WARNING(f"DRY RUN - Would process {len(states_data)} states"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Created: {created_count} states"))
            self.stdout.write(self.style.WARNING(f"↻ Updated: {updated_count} states"))
            self.stdout.write(self.style.SUCCESS(f"Total: {created_count + updated_count} states"))
        self.stdout.write("="*70 + "\n")
        
        if not dry_run:
            self.stdout.write("\nNext steps:")
            self.stdout.write("1. Run: python manage.py makemigrations")
            self.stdout.write("2. Run: python manage.py migrate")
            self.stdout.write("3. Update populate_springfields command to link to State objects")
