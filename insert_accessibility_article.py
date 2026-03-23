import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mocon.settings')
django.setup()
from core.models import Article, City, Site
from django.utils.text import slugify
from django.utils import timezone

city = City.objects.get(pk=2)
site = Site.objects.get(pk=1)

title = "Can You Read the Cardinals Schedule? We Built One That Works for Everyone"
excerpt = (
    "MLB.com uses color alone to show home vs. away games, which disappears in dark mode "
    "and high contrast. We built an accessible Cardinals schedule with text labels alongside "
    "color, fully WCAG 1.4.1 compliant."
)
content = """If you use Windows dark mode or high contrast, try pulling up the official Cardinals schedule at MLB.com.

What you likely see is a calendar full of identical-looking tiles with no way to tell a home game from an away game. The legend? Invisible. The color coding? Gone. Every game looks the same.

This is not a quirk. It is an accessibility failure.

<h2>What WCAG 1.4.1 Says</h2>

The Web Content Accessibility Guidelines (WCAG) 2.1, Success Criterion 1.4.1, is called "Use of Color." It states: <em>"Color is not used as the only visual means of conveying information."</em>

MLB.com's schedule violates this directly. Home, away, and spring training games are differentiated by background color only. No text label on the tile, no icon, no pattern. In dark mode or high contrast mode, those colors collapse to a single system color and the entire legend becomes meaningless.

<h2>Who Does This Affect?</h2>

Approximately 8% of men and 0.5% of women have some form of color vision deficiency. Add users who run high contrast mode due to photosensitivity, low vision, or migraines, plus the growing number of people who simply prefer dark mode, and you have a significant portion of Cardinals fans unable to read their own team's schedule on the official site.

<h2>We Built an Alternative</h2>

We built our own Cardinals schedule view right here on SeekingSpringfield.com using the public MLB Stats API. Every game tile uses a bold text label alongside color:

<ul>
<li><strong>H</strong> = Home game at Busch Stadium (green border)</li>
<li><strong>A</strong> = Away game (blue border)</li>
<li><strong>ST</strong> = Spring Training (amber border)</li>
</ul>

The legend never disappears. Screen readers announce the full game context. The calendar works in every color mode on every device.

<a href="/cardinals-schedule/" class="font-semibold underline">View the Accessible Cardinals Schedule here.</a>

<h2>Why This Matters Beyond Baseball</h2>

Accessibility is not optional polish. It is baseline engineering. Security, accessibility, and transparency before all else. When a public-facing website fails WCAG 2.1 Level AA, it is excluding real users with real needs.

The fix is straightforward: add a text label to each game tile. "H" for home, "A" for away. Two characters. That is all it takes. We will keep building tools that work for everyone. That is what technology enablement means."""

slug = slugify(title)
if Article.objects.filter(slug=slug).exists():
    slug = slug + '-wcag'

a = Article.objects.create(
    city=city, site=site,
    title=title, slug=slug,
    excerpt=excerpt, content=content,
    category='TECHNOLOGY',
    ai_generated=False,
    published=True, featured=True,
    published_date=timezone.now().date(),
    meta_description='MLB.com Cardinals schedule fails WCAG 1.4.1 in dark mode and high contrast. We built an accessible alternative with text labels usable by everyone.',
    keywords='Cardinals schedule accessible, WCAG 1.4.1, MLB accessibility, dark mode Cardinals schedule, Springfield',
)
print(f'Article id={a.pk} slug={a.slug}')
print(f'URL: https://seekingspringfield.com/article/{a.slug}/')
