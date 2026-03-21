"""
Seed Springfield MO + Springfield IL — Seeking Springfield city content

Creates:
  - Illinois State record
  - Springfield, Missouri City (pop ~170K — "The Queen City")
  - Springfield, Illinois City (pop ~115K — Abe Lincoln's hometown & IL state capital)
  - seekingspringfield.com Site record (get_or_create)
  - 4 seed articles per Springfield (GUIDE + LIFESTYLE + GOVERNMENT + BUSINESS)

Usage:
    python manage.py seed_springfield_cities
    python manage.py seed_springfield_cities --dry-run
    python manage.py seed_springfield_cities --city mo      # MO only
    python manage.py seed_springfield_cities --city il      # IL only
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
import datetime


class Command(BaseCommand):
    help = 'Seed Springfield MO + IL cities with launch content for Seeking Springfield'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be created without saving to database',
        )
        parser.add_argument(
            '--city',
            choices=['mo', 'il', 'both'],
            default='both',
            help='Which Springfield to seed (default: both)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        city_filter = options['city']

        self.stdout.write('=' * 72)
        self.stdout.write('SEED SPRINGFIELD CITIES — SEEKING SPRINGFIELD')
        self.stdout.write('=' * 72)

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN — nothing will be saved\n'))

        from core.models import Site, State, City, Article

        # ── Seeking Springfield Site ──────────────────────────────────────────
        self.stdout.write('\n[1/6] Seeking Springfield site record')
        if not dry_run:
            ss_site, created = Site.objects.get_or_create(
                domain_name='seekingspringfield.com',
                defaults={
                    'site_type': 'SEEKING',
                    'display_name': 'Seeking Springfield',
                    'primary_color': '#0078D4',
                    'is_active': True,
                    'launch_date': datetime.date.today(),
                },
            )
            verb = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'  {verb}: seekingspringfield.com'))
        else:
            self.stdout.write('  Would get_or_create: seekingspringfield.com')
            ss_site = None

        # ── Missouri State ────────────────────────────────────────────────────
        self.stdout.write('\n[2/6] Missouri state record')
        if not dry_run:
            mo_state, created = State.objects.get_or_create(
                abbreviation='MO',
                defaults={
                    'name': 'Missouri',
                    'capital': 'Jefferson City',
                    'state_flower': 'White Hawthorn Blossom',
                    'state_tree': 'Flowering Dogwood',
                    'state_bird': 'Eastern Bluebird',
                    'state_motto': 'Salus populi suprema lex esto',
                    'region': 'Midwest',
                },
            )
            verb = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'  {verb}: Missouri (MO)'))
        else:
            self.stdout.write('  Would get_or_create: Missouri (MO)')
            mo_state = None

        # ── Illinois State ────────────────────────────────────────────────────
        self.stdout.write('\n[3/6] Illinois state record')
        if not dry_run:
            il_state, created = State.objects.get_or_create(
                abbreviation='IL',
                defaults={
                    'name': 'Illinois',
                    'capital': 'Springfield',
                    'state_flower': 'Violet',
                    'state_tree': 'White Oak',
                    'state_bird': 'Northern Cardinal',
                    'state_motto': 'State sovereignty, national union',
                    'region': 'Midwest',
                },
            )
            verb = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'  {verb}: Illinois (IL)'))
        else:
            self.stdout.write('  Would get_or_create: Illinois (IL)')
            il_state = None

        # ── Springfield, Missouri ─────────────────────────────────────────────
        if city_filter in ('mo', 'both'):
            self.stdout.write('\n[4/6] Springfield, Missouri')
            if not dry_run:
                spfld_mo, created = City.objects.get_or_create(
                    name='Springfield',
                    state=mo_state,
                    defaults={
                        'state_abbr': 'MO',
                        'country': 'USA',
                        'population': 169176,
                        'latitude': 37.2090,
                        'longitude': -93.2923,
                    },
                )
                verb = 'Created' if created else 'Already exists'
                self.stdout.write(self.style.SUCCESS(f'  {verb}: Springfield, MO'))

                # Link to seekingspringfield.com site
                spfld_mo.sites.add(ss_site)
                self.stdout.write(f'  Linked to: seekingspringfield.com')

                # Seed articles
                self._seed_springfield_mo_articles(spfld_mo, ss_site, dry_run)
            else:
                self.stdout.write('  Would create: Springfield, Missouri (pop 169,176)')
                self._seed_springfield_mo_articles(None, None, dry_run)
        else:
            self.stdout.write('\n[4/6] Springfield, Missouri — SKIPPED')

        # ── Springfield, Illinois ─────────────────────────────────────────────
        if city_filter in ('il', 'both'):
            self.stdout.write('\n[5/6] Springfield, Illinois')
            if not dry_run:
                spfld_il, created = City.objects.get_or_create(
                    name='Springfield',
                    state=il_state,
                    defaults={
                        'state_abbr': 'IL',
                        'country': 'USA',
                        'population': 114230,
                        'latitude': 39.8014,
                        'longitude': -89.6435,
                    },
                )
                verb = 'Created' if created else 'Already exists'
                self.stdout.write(self.style.SUCCESS(f'  {verb}: Springfield, IL'))

                # Link to seekingspringfield.com site
                spfld_il.sites.add(ss_site)
                self.stdout.write(f'  Linked to: seekingspringfield.com')

                # Seed articles
                self._seed_springfield_il_articles(spfld_il, ss_site, dry_run)
            else:
                self.stdout.write('  Would create: Springfield, Illinois (pop 114,230)')
                self._seed_springfield_il_articles(None, None, dry_run)
        else:
            self.stdout.write('\n[5/6] Springfield, Illinois — SKIPPED')

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write('\n[6/6] Complete')
        self.stdout.write('=' * 72)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN complete — no changes made'))
        else:
            self.stdout.write(self.style.SUCCESS('Springfield cities seeded successfully!'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('  1. Set GA_MEASUREMENT_ID in .env for analytics')
            self.stdout.write('  2. Run: python manage.py runserver 8002')
            self.stdout.write('  3. Visit http://localhost:8002/cities/springfield-mo/')
            self.stdout.write('  4. Visit http://localhost:8002/cities/springfield-il/')

    # ── Springfield MO Articles ───────────────────────────────────────────────

    def _seed_springfield_mo_articles(self, city, site, dry_run):
        from core.models import Article

        articles = [
            {
                'title': "Springfield, Missouri: The Queen City of the Ozarks",
                'slug': 'springfield-mo-city-guide',
                'category': 'GUIDE',
                'excerpt': (
                    "Nestled in the rolling hills of the Ozarks, Springfield Missouri is "
                    "the third-largest city in the state — a college town, outdoor recreation "
                    "hub, and the birthplace of Route 66."
                ),
                'content': """Springfield, Missouri sits at the northern edge of the Ozark Plateau at 1,268 feet above sea level — the highest elevation of any major Missouri city. Named "The Queen City of the Ozarks," it's the cultural and economic center of a 27-county region.

## Population & Geography

With a population of approximately 169,000 (metro area: 470,000), Springfield is Missouri's third-largest city. Greene County encompasses its 83 square miles. The city sits where the Ozark highlands meet the prairie — a landscape that shaped everything from its economy to its cuisine.

## Founding & History

Springfield was platted in 1835, incorporated in 1838, and became the Greene County seat. The Civil War brought fierce fighting here — the First Battle of Springfield (1861) and Second Battle of Springfield (1863) both took place within city limits. The town changed hands multiple times during the war.

The Wild West's founding myth traces directly to Springfield: on July 21, 1865, James Butler "Wild Bill" Hickok faced off against Davis Tutt in the Public Square — the first recorded quick-draw duel in American history. Hickok shot Tutt through the heart at 75 yards.

## Route 66

Springfield holds a special place in travel history: **this is where Route 66 was named**. On April 30, 1926, Cyrus Avery and John Woodruff proposed the number "66" for the new federal highway at the Colonial Hotel in downtown Springfield. The Mother Road ran directly through the city, and several original Route 66 businesses survive today.

## Education

Springfield is home to four major universities:
- **Missouri State University** (enrollment: 23,000) — the city's largest employer
- **Drury University** — private liberal arts, founded 1873
- **Evangel University** — Assemblies of God, founded 1955
- **OTC (Ozarks Technical Community College)** — 13,000 students

## Major Employers

- **Bass Pro Shops** — World headquarters, Springfield (founded by Johnny Morris in 1971)
- **Mercy Health** — 2,000+ physician health system
- **CoxHealth** — Regional health system with 13,000 employees
- **O'Reilly Auto Parts** — National HQ, founded here in 1957
- **Great Southern Bank** — Regional financial institution HQ

## Sports & Recreation

The Springfield Cardinals (AA affiliate of the St. Louis Cardinals) play at **Hammons Field**, a 8,000-seat downtown ballpark. The city has a 117-mile trail system including the Galloway Creek Greenway. Table Rock Lake is 40 miles south — one of the Ozarks' premier recreational lakes.

## Coordinates

37.2090° N, 93.2923° W — Elevation: 1,268 feet""",
                'featured': True,
                'meta_description': (
                    "Complete guide to Springfield, Missouri — population, history, "
                    "Route 66 origins, Bass Pro Shops, and Ozarks outdoor recreation."
                ),
                'keywords': 'Springfield Missouri, Queen City Ozarks, Route 66, Bass Pro Shops, Missouri State University',
            },
            {
                'title': "Bass Pro Shops: How Springfield MO Became the Outdoor Sports Capital",
                'slug': 'springfield-mo-bass-pro-shops-history',
                'category': 'BUSINESS',
                'excerpt': (
                    "Johnny Morris opened a small fishing tackle section in his father's liquor store "
                    "in 1971. Today, Bass Pro Shops is a $6 billion retail empire — and Springfield "
                    "Missouri is its world headquarters."
                ),
                'content': """In 1971, Johnny Morris was 19 years old and passionate about fishing. His father, John A. Morris Sr., owned a liquor store in Springfield called Brown Derby. Johnny talked his father into letting him use a small section of the store to sell fishing tackle.

That 8-foot section became the foundation of Bass Pro Shops.

## From Eight Feet to Eight Acres

The original Brown Derby Liquors location at 1735 S. Campbell Ave is now occupied by the original Bass Pro Shops store — the company never moved. What started as a fishing tackle wall grew into the flagship **Outdoor World store**, now covering 500,000 square feet (8 acres under one roof).

The flagship store receives **4 million visitors per year** — more than any other attraction in Missouri, including the Arch.

Features of the Springfield flagship:
- 500-gallon saltwater aquarium
- 64-foot waterfall
- Indoor archery range
- Antler chandeliers made from naturally shed deer antlers
- Taxidermy displays of world-record fish and game
- Restaurant (Hemingway's Blue Water Café) inside the store

## The Acquisition of Cabela's

In 2017, Bass Pro Shops acquired Cabela's for $4.5 billion — creating the largest outdoor/hunting/fishing retailer in the world. The combined company operates 200+ stores across North America, generates over $6 billion in annual revenue, and has Springfield as its beating heart.

## Johnny Morris's Springfield Legacy

Morris has invested heavily in Springfield beyond retail:
- **Top of the Rock** (Branson area) — golf course, ancient ozarks natural history museum
- **Big Cedar Lodge** — Forbes Four-Star resort, 4,600 acres
- **Dogwood Canyon Nature Park** — 10,000-acre nature preserve
- **Johnny Morris Wonders of Wildlife National Museum & Aquarium** — adjacent to the flagship store, 1.5 million square feet, largest aquarium/museum complex in the U.S.

The Wonders of Wildlife earned the title of **America's Best Aquarium** by USA Today readers in 2019, 2020, and 2021.

## Economic Impact

Bass Pro Shops is Greene County's largest private employer with 2,000+ local jobs. The company's presence — and Morris's ongoing investment in the Springfield region — makes the city a legitimate outdoor recreation destination, not just a retail stop.

For a city of 170,000, Springfield punches far above its weight in tourism and outdoor economy.""",
                'featured': False,
                'meta_description': (
                    "How Johnny Morris turned an 8-foot fishing tackle section into Bass Pro Shops "
                    "— Springfield Missouri's billion-dollar outdoor retail empire."
                ),
                'keywords': 'Bass Pro Shops Springfield Missouri, Johnny Morris, outdoor retail, Cabela\'s acquisition',
            },
            {
                'title': "Wild Bill Hickok and the First Quick-Draw Duel in American History",
                'slug': 'springfield-mo-wild-bill-hickok-duel',
                'category': 'LIFESTYLE',
                'excerpt': (
                    "On July 21, 1865, James Butler Hickok shot Davis Tutt through the heart "
                    "at 75 yards in Springfield's Public Square. It was the first recorded "
                    "quick-draw duel in the American West."
                ),
                'content': """Springfield, Missouri is the birthplace of the classic Western duel — not Tombstone, not Dodge City. It happened here, in the Public Square, on a hot July afternoon in 1865.

## The Backstory

James Butler "Wild Bill" Hickok had been in Springfield for several months following his service as a Union scout during the Civil War. He was a gambler, a lawman-in-training, and a man of considerable reputation with a pistol.

Davis Tutt was a former Confederate soldier. The two men had an ongoing dispute over gambling debts — specifically, Hickok owed Tutt $35. Tutt claimed the debt was $45.

Tutt took Hickok's prized Waltham pocket watch as collateral. He planned to wear it publicly the next day — a deliberate insult.

## The Duel

On the morning of July 21, 1865, Hickok warned Tutt not to wear the watch in public. Tutt ignored him.

At approximately 6:00 PM, both men stood in the Public Square. The distance between them: 75 yards. Both men drew simultaneously.

Tutt **missed**. Hickok **did not**. The ball passed through Tutt's side between his ribs. He staggered, groaned "Boys, I'm killed," took a few steps toward the courthouse, and collapsed dead.

## Why This Matters

The encounter established several elements that would define the mythology of the American West for the next 150 years:

- **Standing face to face** — both men in the open, equal footing
- **Quick-draw from the hip** — not aiming down the barrel
- **A point of honor** — not assassination, robbery, or ambush
- **Public witnesses** — the square was filled with onlookers

Every Western movie duel since 1865 draws on the Springfield template.

## What Happened to Hickok

Hickok was tried for manslaughter and acquitted — the jury ruled it "self-defense in a row." He went on to serve as marshal of Abilene, Kansas, and was killed in Deadwood, Dakota Territory in 1876 while holding a poker hand of aces and eights (the "Dead Man's Hand").

## Visit Today

A historical marker in **Park Central Square** in downtown Springfield commemorates the duel. The exact location where Hickok stood is marked. The square has been redesigned many times since 1865 but remains the civic heart of downtown Springfield.""",
                'featured': False,
                'meta_description': (
                    "The story of Wild Bill Hickok's 1865 quick-draw duel in Springfield Missouri "
                    "— the first recorded gunfight of the American West."
                ),
                'keywords': 'Wild Bill Hickok Springfield Missouri, first quick-draw duel, Davis Tutt, American West history',
            },
            {
                'title': "Missouri State University: Springfield's Academic Anchor",
                'slug': 'springfield-mo-missouri-state-university',
                'category': 'EDUCATION',
                'excerpt': (
                    "Founded in 1905, Missouri State University enrolls 23,000 students and "
                    "is Springfield's largest employer. Its statewide mission in public affairs "
                    "makes it unique among Missouri's research universities."
                ),
                'content': """Missouri State University, founded in 1905 as the Fourth District Normal School, is today a doctoral-level public university with a statewide mission in public affairs education — a unique mandate in Missouri's higher education system.

## By the Numbers

- **Enrollment:** 23,500 students (main campus)
- **Faculty:** 900+ full-time faculty
- **Colleges:** 9 academic colleges
- **Degrees offered:** 200+ undergraduate, 60+ graduate programs
- **Largest employer in Springfield:** 5,000+ employees
- **Annual economic impact:** $1.8 billion to the Springfield metro area

## The Public Affairs Mission

Missouri State's statewide mission in **public affairs** — ethical leadership, cultural competence, and community engagement — permeates its curriculum in ways that distinguish it from regional comprehensive universities. Every degree program incorporates a public affairs component.

## Notable Programs

- **College of Business** — AACSB accredited, strong supply chain and entrepreneurship programs
- **Kinesiology** — consistently ranked among the best undergraduate programs in the Midwest
- **Communication** — KSMU public radio and OZTV student television
- **Agriculture** — Farm operations at William H. Darr College of Agriculture

## Bear Athletics

Missouri State Bears compete in NCAA Division I (Missouri Valley Conference). Sports include football (Plaster Stadium), basketball (Great Southern Bank Arena — 11,000 seats), and baseball (Hammons Field, shared with the Springfield Cardinals AA team).

## Campus Geography

The main campus sprawls across 225 acres on the south side of Springfield. The characteristic red-brick Georgian architecture gives the campus a cohesive aesthetic despite buildings spanning 115 years. The Jordan Valley Innovation Center connects campus research to downtown entrepreneurship.

## Springfield's College Town Economy

With four universities and 50,000+ college students, Springfield has a year-round college economy that buffers it from manufacturing cycles. The student population supports a dense restaurant and entertainment corridor along Commercial Street and Battlefield Road.""",
                'featured': False,
                'meta_description': (
                    "Missouri State University in Springfield — public affairs mission, "
                    "23,000 students, largest employer, and anchor of the city's college economy."
                ),
                'keywords': 'Missouri State University Springfield, MSU Bears, public affairs mission, college town Springfield MO',
            },
        ]

        self._write_articles(articles, city, site, dry_run, 'Springfield MO')

    # ── Springfield IL Articles ───────────────────────────────────────────────

    def _seed_springfield_il_articles(self, city, site, dry_run):
        from core.models import Article

        articles = [
            {
                'title': "Springfield, Illinois: Abraham Lincoln's Hometown and the Prairie State Capital",
                'slug': 'springfield-il-city-guide',
                'category': 'GUIDE',
                'excerpt': (
                    "Springfield, Illinois has been the state capital since 1837 and Abraham Lincoln's "
                    "home since 1837. Today it's a city of 115,000 where the 16th president's shadow "
                    "falls on nearly every block."
                ),
                'content': """Springfield, Illinois is one of America's most historically significant small cities. It has been the state capital for 187 years and was home to Abraham Lincoln for 24 years — longer than anywhere else he lived.

## Geography & Population

Springfield sits in central Illinois on the Sangamon River at 597 feet elevation. Population: approximately 114,000 (metro area: 210,000). It's the capital of Illinois and the seat of Sangamon County.

The city lies at the agricultural center of the state — surrounded by the richest farmland in America. The flat prairie landscape here is a complete contrast to the rugged Ozark terrain of Springfield, Missouri.

## Capital City

Springfield became the Illinois state capital in 1837, replacing Vandalia. Abraham Lincoln, then a young state legislator, was among the most vocal advocates for moving the capital to Springfield.

The **Illinois State Capitol** building, completed in 1888, rises 361 feet — taller than the U.S. Capitol dome. The building's Renaissance-style architecture makes it one of the most beautiful state capitols in America.

State government is Springfield's dominant employer, with approximately 20,000 state workers in the area.

## Abraham Lincoln's Springfield

Lincoln lived in Springfield from 1837 to 1861. His Springfield years encompassed his entire law career, his courtship and marriage to Mary Todd, the birth of four sons, and his rise from obscure state legislator to president-elect of the United States.

Key Lincoln sites:
- **Abraham Lincoln Presidential Library & Museum** — One of the most advanced presidential museums in the country; opened 2005
- **Lincoln Home National Historic Site** — The only home Lincoln ever owned; maintained by the National Park Service
- **Lincoln's Tomb** — Oak Ridge Cemetery; Lincoln, Mary Todd, and three of their sons are interred here
- **Lincoln-Herndon Law Offices** — Where Lincoln practiced law from 1843-1852
- **Old State Capitol** — Where Lincoln delivered the "House Divided" speech on June 16, 1858

## Founding & History

Springfield was platted in 1821. The Sangamon County seat since 1821, it grew rapidly as Illinois's population exploded in the 1820s and 1830s. By the time Lincoln arrived in 1837, Springfield had 1,500 residents and was already the most prosperous town in central Illinois.

The city saw no Civil War combat, but it sent thousands of soldiers and Lincoln himself departed from the Great Western Railway depot on February 11, 1861, for Washington — never to return alive.

## Modern Springfield

Beyond Lincoln tourism, Springfield has a diversified economy anchored by state government, healthcare (Memorial Medical Center, HSHS St. John's), and education (University of Illinois Springfield, Lincoln Land Community College).

The city has invested heavily in its historic downtown, and the Route 66 corridor through Springfield is among the best-preserved stretches of the Mother Road.

## Coordinates

39.8014° N, 89.6435° W — Elevation: 597 feet""",
                'featured': True,
                'meta_description': (
                    "Complete guide to Springfield Illinois — Abraham Lincoln's hometown, "
                    "state capital since 1837, presidential library, and Illinois history."
                ),
                'keywords': 'Springfield Illinois, Abraham Lincoln hometown, Illinois state capital, Lincoln Presidential Library',
            },
            {
                'title': "The Lincoln Home: America's Most Visited Presidential Historic Site",
                'slug': 'springfield-il-lincoln-home',
                'category': 'LIFESTYLE',
                'excerpt': (
                    "At 8th and Jackson in downtown Springfield sits a modest frame house "
                    "where Abraham Lincoln lived for 17 years and raised his family. "
                    "It's the only home he ever owned."
                ),
                'content': """The Lincoln Home at 426 South Seventh Street in Springfield is one of the most emotionally affecting historic sites in America. It's modest — a story-and-a-half Greek Revival house, white clapboard, green shutters — the kind of house a successful country lawyer might own. That's exactly what Abraham Lincoln was when he bought it.

## Purchase & Years There

Lincoln purchased the house in 1844 for $1,500 (and a promissory note) from Reverend Charles Dresser, the minister who had married him and Mary Todd two years earlier. He paid $1,200 in cash and transferred a small piece of downtown commercial property worth $300 as the balance.

Lincoln lived here from January 1844 until February 1861 — 17 years. When he left for Washington after winning the 1860 election, he sold the furniture, rented the house for $350/year, and locked the door.

He never came back.

## The House Itself

When Lincoln bought it, the house was a story-and-a-half cottage. By the time he left, it had been expanded to a full two stories to accommodate the growing Lincoln family (four sons: Robert, Edward, William "Willie," and Thomas "Tad").

The ground floor contains:
- **Parlor** — Where Lincoln entertained political visitors and held private meetings
- **Sitting room** — Family gathering space
- **Kitchen** — Mary Todd's domain; she was known as an excellent cook
- **Bed chamber** — Abraham and Mary's room

The second floor contains the boys' rooms and additional guest space.

## The Neighborhood

The National Park Service manages not just the house but the entire surrounding four-block neighborhood — 12 acres in the heart of Springfield. The cobblestone streets around the Lincoln Home are closed to vehicle traffic. The block on which the house stands retains much of its 1860 character.

## Visiting

The Lincoln Home is **free to visit** and managed by the National Park Service. Timed entrance tickets (also free) are required for house tours. The visitor center at 426 S. 7th Street provides historical context before entry.

Open year-round except Thanksgiving, Christmas, and New Year's Day.

## The Farewell Speech

On the morning of February 11, 1861, Lincoln stood on the rear platform of his train at the Great Western Railway depot and delivered one of the shortest and most moving speeches of his career:

*"I now leave, not knowing when, or whether ever, I may return, with a task before me greater than that which rested upon Washington. Without the assistance of that Divine Being, who ever attended him, I cannot succeed. With that assistance I cannot fail."*

The depot building no longer stands, but a marker commemorates the site at 10th and Monroe in Springfield.""",
                'featured': False,
                'meta_description': (
                    "Visit the Lincoln Home in Springfield Illinois — the only house Abraham "
                    "Lincoln ever owned, now a free National Park Service historic site."
                ),
                'keywords': 'Lincoln Home Springfield Illinois, Abraham Lincoln historic site, National Park Service Springfield, 1844 Lincoln house',
            },
            {
                'title': "Illinois State Capitol: One of America's Most Beautiful Domes",
                'slug': 'springfield-il-state-capitol',
                'category': 'GOVERNMENT',
                'excerpt': (
                    "Completed in 1888, the Illinois State Capitol stands 361 feet tall — "
                    "taller than the U.S. Capitol. Its zinc-and-iron dome dominates the "
                    "Springfield skyline and anchors the city's government district."
                ),
                'content': """The Illinois State Capitol is one of the most architecturally distinguished government buildings in the United States — and it's taller than the dome of the U.S. Capitol in Washington.

## Height & Architecture

The building stands **361 feet** from ground to tip of the flagpole — 14 feet taller than the U.S. Capitol dome (which tops out at 287 feet to the base of the Statue of Freedom, 289 feet with the statue).

The style is French Renaissance — grand, symmetrical, and commanding in the flat Illinois prairie. The dome is clad in zinc and iron with interior frescoes by German artist Johannes Oertel.

Cornerstone: November 5, 1868  
Completed: 1888  
Cost: $4.5 million (1888 dollars)  
Architect: Alfred Piquenard (original design); later John C. Cochrane and William Boyington

## The Old State Capitol

The current building is Springfield's **second** state capitol. The Old State Capitol, just a few blocks away at the center of the downtown square, served from 1837 to 1876. This is where Lincoln served as a state legislator, where he argued cases before the Illinois Supreme Court, and where he delivered the famous **"House Divided" speech** on June 16, 1858, accepting the Republican nomination for U.S. Senate:

*"A house divided against itself cannot stand. I believe this government cannot endure, permanently, half slave and half free."*

Lincoln lost that Senate race to Stephen Douglas, but the Lincoln-Douglas debates that followed made him a national figure and positioned him for the 1860 presidential run.

## Today's Capitol Complex

The Capitol complex covers several city blocks and includes:
- **Illinois State Capitol Building** — House and Senate chambers, governor's office
- **Illinois State Library** — Giles Filley collection, Lincoln documents
- **Illinois State Museum** — Natural and cultural history of Illinois
- **Centennial Building** — State administrative offices

## Visiting

Free public tours of the State Capitol operate Monday through Friday during legislative sessions. The ground floor rotunda is particularly impressive — the interior dome rises 237 feet from the floor and is decorated with portraits of past Illinois governors and military scenes.

The view from outside, looking up at the dome against the prairie sky, is one of the more dramatic sights in Midwest civic architecture.""",
                'featured': False,
                'meta_description': (
                    "Illinois State Capitol in Springfield — taller than the U.S. Capitol dome, "
                    "completed 1888, and site of Lincoln's famous House Divided speech."
                ),
                'keywords': 'Illinois State Capitol Springfield, government building, Lincoln House Divided speech, French Renaissance dome',
            },
            {
                'title': "Route 66 in Springfield Illinois: The Mother Road's Prairie Stretch",
                'slug': 'springfield-il-route-66',
                'category': 'LIFESTYLE',
                'excerpt': (
                    "Route 66 runs directly through downtown Springfield Illinois, and this "
                    "stretch preserves some of the Mother Road's most authentic mid-century "
                    "diners, motels, and Americana."
                ),
                'content': """Route 66 enters Springfield from the west on Peoria Road, cuts through the downtown, and exits toward Chicago on Ninth Street. This central Illinois stretch is among the best-preserved sections of the original highway.

## Springfield's Route 66 Corridor

Unlike many Route 66 cities where the highway bypasses the downtown, the Springfield alignment runs directly through the city center. This means travelers driving the original alignment pass within two blocks of the State Capitol and the Lincoln Home.

Key landmarks on the Springfield alignment:

**Cozy Dog Drive In** (2935 S. Sixth Street)  
The original home of the corn dog on a stick — or at least the "Cozy Dog," as proprietor Ed Waldmire Jr. called it when he opened in 1949. The Waldmire family sold the restaurant to the public in 2022, but the building and its Route 66 murals remain.

**Maid-Rite Sandwich Shop** (118 N. Pasfield Street)  
A surviving original loose-meat sandwich shop on the historic alignment. Maid-Rite is a Midwest chain, but Springfield's location occupies a building from the Route 66 era.

**Motorists Hotel / Vickers Oil Station remnants**  
Several early automotive service structures remain along the original South Sixth Street alignment, many converted to other uses but retaining their 1930s-1950s architectural character.

## The Springfield Connection to Route 66's Origins

While Route 66 was *named* in Springfield, Missouri (where Cyrus Avery and John Woodruff proposed "66" at the Colonial Hotel), Illinois had an equally critical role: Illinois Governor Len Small signed the first statewide road sign legislation that enabled the federal highway's marking and maintenance.

## Route 66 Heritage Museum

The **Illinois Route 66 Heritage Museum** in Pontiac (90 minutes north of Springfield) is the state's primary archive for the highway's history, but Springfield's Illinois Route 66 Association maintains walking tour maps that cover the full Springfield alignment.

## Driving the Alignment

From St. Louis to Springfield: Interstate 55 follows the old Route 66 alignment almost exactly for this 100-mile stretch. Exits for Litchfield, Staunton, Girard, Carlinville, and Virden will take you off the expressway onto surviving stretches of original two-lane highway.

Springfield to Chicago: The northern alignment through Pontiac, Joliet, and Cicero preserves more original road surface than the southern stretch, with numerous surviving neon signs, vintage motels, and roadside attractions.""",
                'featured': False,
                'meta_description': (
                    "Route 66 through Springfield Illinois — surviving diners, motels, "
                    "and mid-century Americana along the Mother Road's prairie stretch."
                ),
                'keywords': 'Route 66 Springfield Illinois, Cozy Dog Drive In, Mother Road Illinois, historic highway Springfield IL',
            },
        ]

        self._write_articles(articles, city, site, dry_run, 'Springfield IL')

    # ── Shared article writer ─────────────────────────────────────────────────

    def _write_articles(self, articles, city, site, dry_run, label):
        from core.models import Article

        self.stdout.write(f'\n  Articles for {label}:')
        for art in articles:
            if dry_run:
                self.stdout.write(f'    Would create: {art["title"][:60]}...')
                continue

            _, created = Article.objects.get_or_create(
                slug=art['slug'],
                defaults={
                    'city': city,
                    'site': site,
                    'title': art['title'],
                    'content': art['content'],
                    'excerpt': art['excerpt'],
                    'category': art['category'],
                    'featured': art.get('featured', False),
                    'meta_description': art.get('meta_description', ''),
                    'keywords': art.get('keywords', ''),
                    'ai_generated': False,
                    'ai_model_used': 'human-authored',
                    'published': True,
                    'published_date': timezone.now(),
                },
            )
            verb = 'Created' if created else 'Exists '
            self.stdout.write(self.style.SUCCESS(f'    {verb}: {art["title"][:60]}'))
