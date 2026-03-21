# MissouriConstruction.com - AI Content Engine

**Master Django Framework for Multi-Site City Directories**

Built by Gregory Woodruff | Cloud and Secure Limited  
Course: [YouBetYourAzure.com](https://youbetyourazure.com)

---

## 🎯 What is This?

MissouriConstruction.com is the **master Django framework** that powers multiple city directory websites from a single codebase:

- **SeekingSpringfield.com** - 24 Springfield cities across the US
- **SeekingWashington.com** - 88 Washington cities
- **SeekingFranklin.com** - 30 Franklin cities
- **MissouriConstruction.com** - Construction contractors directory
- **LandscapingStLouis.com** - Landscaping businesses directory
- ...and more!

**Total Scale:** 228+ cities, 6+ sites, all managed from one admin interface.

---

## 🏗️ Architecture Overview

### Foundation (Complete ✅)

**Core Models:**
- `Site` - Each domain (seekingspringfield.com, etc.)
- `City` - 228 cities with demographics from Census API
- `Article` - AI-generated content (city guides, demographics, tourism)
- `Business` - Directory listings (free, premium, featured tiers)
- `Event` - Upcoming events and conventions
- `ContentPerformance` - Daily analytics tracking

**Why This Design?**
- **One database** stores all cities, articles, and businesses
- **One admin interface** manages all sites
- **Same article** can be published to multiple sites
- **Census data** shared across all sites (fetch once, use everywhere)

### Data Layer (Complete ✅)

**Census API Integration:**
- Bulletproof error handling (5 layers)
- Retry logic with exponential backoff
- 14 Census variables (population, income, education, etc.)
- Management command: `fetch_census_data`

**AI Content Engine:**
- Data aggregation from multiple sources
- GPT-4 integration for article generation
- Modular design (easy to add new data sources)
- Management command: `generate_daily_content`

**Export Capabilities:**
- CSV export for Excel
- Power BI optimized format
- JSON export for API consumption
- Management command: `export_census_data`

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Navigate to project
cd "missouriconstruction.com"

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit .env file:**
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Census Bureau API (free)
CENSUS_API_KEY=your-census-api-key

# OpenAI API (required for AI content)
OPENAI_API_KEY=sk-proj-your-key-here

# Google Analytics (optional)
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

### 2. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: admin
# Email: your-email@example.com
# Password: (choose secure password)
```

### 3. Populate Springfield Cities

```bash
# Add all 24 Springfields
python manage.py populate_springfields

# Output:
# ✅ Created site: seekingspringfield.com
# ✅ Created: Springfield, IL
# ✅ Created: Springfield, MO
# ... (22 more)
# Total: 24 cities
```

### 4. Fetch Census Data

```bash
# Fetch demographics for all Springfields
python manage.py fetch_census_data --site seekingspringfield.com

# Output:
# [1/24] Processing: Springfield, Illinois
# ✅ Population: 114,394 | Median Income: $62,000
# [2/24] Processing: Springfield, Missouri
# ✅ Population: 168,122 | Median Income: $45,000
# ... (22 more)
#
# Updated: 24
# Skipped: 0
# Errors: 0
# Total Population: 1,234,567
```

**Pro Tip:** Get free Census API key at [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)

### 5. Generate AI Content

```bash
# Generate 3 articles for testing
python manage.py generate_daily_content \
  --site seekingspringfield.com \
  --type city_guide \
  --count 3

# Output:
# [1/24] Processing: Springfield, Illinois
# 🤖 Generating city_guide article...
# ✅ Generated 587 words (2,341 tokens, Quality: 89%)
# [2/24] Processing: Springfield, Missouri
# ✅ Generated 612 words (2,453 tokens, Quality: 92%)
# [3/24] Processing: Springfield, Massachusetts
# ✅ Generated 595 words (2,387 tokens, Quality: 88%)
#
# Articles Generated: 3
# Total Words: 1,794
# Total Tokens: 7,181
# Estimated Cost: $0.32
```

**Important:** Articles are created as **UNPUBLISHED** - review in admin before publishing!

### 6. Review in Admin

```bash
# Start development server
python manage.py runserver 8002

# Open in browser:
# http://localhost:8002/admin/
#
# Login with superuser credentials
```

**Admin Sections:**
- **Sites** - Manage domains and branding
- **Cities** - View all 24 Springfields with Census data
- **Articles** - Review AI-generated content before publishing
- **Businesses** - Add directory listings (premium revenue!)
- **Events** - Upcoming conventions and gatherings
- **Content Performance** - Daily analytics

### 7. Export for Power BI

```bash
# Export Springfields for visualization
python manage.py export_census_data \
  --site seekingspringfield.com \
  --format powerbi \
  --include-articles

# Output:
# 💾 Saved 24 cities to Power BI CSV
# 
# Output: seekingspringfield_20260226.csv
#
# Import to Power BI Desktop:
# 1. Get Data > Text/CSV
# 2. Select file
# 3. Create visualizations (maps, charts, tables)
```

---

## 📊 Management Commands Reference

### populate_springfields

Add all 24 Springfield cities to database and link to seekingspringfield.com.

```bash
# Create all cities
python manage.py populate_springfields

# Preview without creating
python manage.py populate_springfields --dry-run
```

**Output:**
- Creates seekingspringfield.com site (if doesn't exist)
- Creates 24 Springfield cities (if don't exist)
- Links all cities to site via M2M relationship

### fetch_census_data

Fetch demographic data from U.S. Census Bureau API.

```bash
# Fetch for all cities
python manage.py fetch_census_data

# Fetch for specific site
python manage.py fetch_census_data --site seekingspringfield.com

# Fetch for one city
python manage.py fetch_census_data --city "Springfield, IL"

# Overwrite existing data
python manage.py fetch_census_data --force

# Test without making changes
python manage.py fetch_census_data --dry-run

# Use specific API key
python manage.py fetch_census_data --api-key YOUR_KEY_HERE
```

**Options:**
- `--site` - Filter by site domain
- `--city` - Specific city ("City Name, ST" format)
- `--force` - Overwrite existing Census data
- `--dry-run` - Preview without database changes
- `--api-key` - Override environment variable

**Data Fetched:**
- Total population
- Median household income
- Median home value
- Median age
- Unemployment rate
- College education rate
- Homeownership rate
- Race/ethnicity breakdown
- ...and more (14 variables total)

### generate_daily_content

Generate AI-powered articles using GPT-4.

```bash
# Generate 1 article for all cities
python manage.py generate_daily_content

# Generate for specific site
python manage.py generate_daily_content --site seekingspringfield.com

# Generate specific article type
python manage.py generate_daily_content --type tourism

# Generate 10 articles (batch)
python manage.py generate_daily_content --count 10

# Test without spending money
python manage.py generate_daily_content --dry-run

# Use specific API key
python manage.py generate_daily_content --api-key sk-proj-...
```

**Options:**
- `--site` - Filter by site domain
- `--city` - Specific city ("City Name, ST" format)
- `--count` - Articles to generate per city (default: 1)
- `--type` - Article type: city_guide, demographics, tourism, living_here
- `--dry-run` - Preview without creating articles
- `--force` - Generate even if article exists
- `--api-key` - Override environment variable

**Article Types:**

1. **city_guide** - Comprehensive overview (500-800 words)
   - SEO: "Springfield Illinois city guide"
   - Audience: People considering moving or visiting

2. **demographics** - Data-heavy analysis (300-500 words)
   - SEO: "Springfield demographics"
   - Audience: Businesses, investors, researchers

3. **tourism** - Visitor-focused (400-600 words)
   - SEO: "things to do in Springfield"
   - Audience: Tourists, convention attendees

4. **living_here** - Lifestyle quality (500-700 words)
   - SEO: "living in Springfield Illinois"
   - Audience: Potential residents

**Cost:** ~$0.10-0.30 per article (GPT-4 pricing)

### export_census_data

Export city data for visualization and analysis.

```bash
# Export to CSV
python manage.py export_census_data --format csv

# Export for Power BI
python manage.py export_census_data --format powerbi

# Export to Excel
python manage.py export_census_data --format excel

# Export to JSON
python manage.py export_census_data --format json

# Export specific site
python manage.py export_census_data \
  --site seekingspringfield.com \
  --format powerbi

# Include article counts
python manage.py export_census_data \
  --format csv \
  --include-articles

# Include business revenue
python manage.py export_census_data \
  --format csv \
  --include-businesses

# Custom output filename
python manage.py export_census_data \
  --format csv \
  --output my_data.csv
```

**Options:**
- `--format` - csv, excel, json, powerbi (default: csv)
- `--site` - Filter by site domain
- `--output` - Custom filename (default: auto-generated)
- `--include-articles` - Add article count and performance
- `--include-businesses` - Add business count and revenue

**Output Columns:**
- City, State, Country
- Population
- Median Income
- Median Home Value
- Median Age
- Unemployment Rate
- College Education Rate
- Homeownership Rate
- Last Updated
- (Optional) Article Count, Published Articles
- (Optional) Business Count, Premium Businesses, Monthly Revenue

---

## 💰 Revenue Streams

### 1. AdSense (Passive Income)

**Model:** Display ads on high-traffic city pages

**Calculation:**
- 228 cities × 30 articles each = 6,840 pages
- Average 50 views/page/month = 342,000 page views
- RPM (revenue per 1,000 views) = $2-5
- **Monthly Revenue: $684-1,710**

**Optimization:**
- Publish 100+ articles per site for better RPM
- Focus on high-traffic cities (Springfield IL, Springfield MO)
- SEO optimize for "Springfield demographics", "things to do in Springfield"

### 2. Premium Business Listings

**Model:** 3-tier directory pricing

**Tiers:**
- **FREE:** Basic listing (name, address, phone)
- **PREMIUM ($50/month):** Logo, photos, description, analytics access
- **FEATURED ($150/month):** Homepage spotlight, priority search placement

**Calculation:**
- 228 cities × 5 businesses each = 1,140 listings
- 5% pay premium = 57 businesses × $50 = $2,850/month
- 2% pay featured = 23 businesses × $150 = $3,450/month
- **Monthly Revenue: $6,300**

**Target Markets:**
- Construction contractors (MissouriConstruction.com)
- Landscaping companies (LandscapingStLouis.com)
- Real estate agents (all Seeking* sites)
- Local restaurants (tourism angle)

### 3. Data Reports (High Margin)

**Model:** Sell custom Power BI dashboards and CSV exports

**Products:**
- **City Comparison Report:** $500 (all 24 Springfields side-by-side)
- **Demographic Analysis:** $300 (deep dive into one city)
- **Market Research Package:** $1,000 (custom data + visualization)
- **Subscription Dashboard:** $50/month (auto-updates with new Census data)

**Target Customers:**
- Real estate agents (site selection for clients)
- Economic development offices (attract businesses)
- MBA students (case study data)
- Consultants (client deliverables)

**Calculation:**
- 10 reports/month × $500 average = $5,000/month
- **Annual Revenue: $60,000**

### 4. Educational Content (Traffic + Leads)

**Model:** Document everything we build as courses on YouBetYourAzure.com

**Courses:**
1. **Census API Integration** - $49
2. **AI Content Generation** - $99
3. **Power BI Visualization** - $149
4. **Multi-Site Django** - $199

**Revenue:**
- 1,000 students/year × $99 average = $99,000
- Consulting leads: 10 clients × $5,000 = $50,000
- **Annual Revenue: $149,000**

**Strategy:** "30 minutes documentation per 8 hours coding" = 3X revenue multiplier

---

## 📈 Scaling Strategy

### Phase 1: Validate with Springfields (Current)

- ✅ Build infrastructure (Django, Census API, AI engine)
- ✅ Populate 24 Springfield cities
- ✅ Generate 100 articles (test quality)
- 🔄 Deploy to Azure with PostgreSQL
- 🔄 Enable AdSense (need traffic first)
- 🔄 Publish 5-10 articles/day until 500+ published
- 🔄 Monitor: Which cities get most traffic?

**Goal:** Validate business model with one site before scaling to 6 sites.

### Phase 2: Expand to All 6 "Seeking" Sites

- SeekingSpringfield.com (24 cities) ✅ CURRENT
- SeekingWashington.com (88 cities)
- SeekingFranklin.com (30 cities)
- SeekingBristol.com (20 cities)
- SeekingClinton.com (32 cities)
- SeekingGreenville.com (34 cities)

**Total:** 228 cities across 6 domains

**Content Generation:**
- 228 cities × 1 article/day = 228 articles/day (automated!)
- 228 articles/day × 365 days = 83,220 articles/year
- At conservative 1,000 views/article = 83 million page views/year potential

### Phase 3: Add Industry Directories

- MissouriConstruction.com (contractors)
- LandscapingStLouis.com (landscapers)
- (Future) PlumbingChicago.com, ElectricianMiami.com, etc.

**Revenue:** Premium business listings ($50-150/month × 1,000+ businesses)

### Phase 4: Data as a Service

- API access to Census data (developers pay $99/month)
- Custom Power BI dashboards ($500-5,000 each)
- White-label city portals (municipalities pay $500/month)

---

## 🎓 Educational Content Strategy

### "Build While We Document" Philosophy

**Principle:** Every hour of coding = 7.5 minutes of documentation

**ROI:** 12.5% time overhead for 3X revenue multiplier (25X ROI!)

**Implementation:**
- Hour 1-2: Build feature (Census API)
- Minute 90-105: Document as course module
- Hour 3-4: Build next feature (AI engine)
- Minute 210-225: Document as course module

**Result:**
- Production code for our sites
- Educational content for students
- Consulting leads from course graduates
- Repositories of tribal knowledge

### Current Course Modules

1. **CENSUS_API_COURSE_MODULE.md** ✅
   - 8 modules covering Census API integration
   - Lab exercises and real-world use cases
   - Business applications and pricing strategies

2. **AI_CONTENT_ENGINE_COURSE_MODULE.md** ✅
   - Building modular data aggregators
   - Prompt engineering for quality content
   - Power BI export and visualization
   - Error handling and cost management

### Future Course Modules (Planned)

3. **Multi-Site Django Architecture** (Q2 2026)
4. **AdSense Optimization** (Q2 2026)
5. **Premium Listing Sales Funnel** (Q3 2026)
6. **Restaurant & Business Scraping** (Q3 2026)
7. **School District Rankings Integration** (Q3 2026)
8. **Seasonal Content Automation** (Q4 2026)

---

## 🔧 Technical Details

### Project Structure

```
missouriconstruction.com/
├── mocon/                          # Django project
│   ├── settings.py                 # Configuration
│   ├── urls.py                     # URL routing
│   └── wsgi.py                     # WSGI for deployment
│
├── core/                           # Shared models and logic
│   ├── models.py                   # 6 core models
│   ├── admin.py                    # Admin interface
│   ├── census_api.py               # Census API client
│   ├── ai_content_engine.py        # AI content generation
│   └── management/
│       └── commands/
│           ├── fetch_census_data.py
│           ├── generate_daily_content.py
│           ├── export_census_data.py
│           └── populate_springfields.py
│
├── sites/                          # Site-specific logic (future)
├── ai_engine/                      # AI engine (future expansion)
│
├── templates/                      # HTML templates (to be built)
│   ├── base/
│   │   ├── base.html              # Shared layout
│   │   ├── city_home.html         # City landing page
│   │   └── article.html           # Article display
│   └── ...
│
├── static/                         # CSS, JS, images (to be built)
├── media/                          # User uploads (logos, photos)
│
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git exclusions
├── manage.py                       # Django CLI
│
└── Documentation/
    ├── README.md                   # This file
    ├── CENSUS_API_COURSE_MODULE.md
    └── AI_CONTENT_ENGINE_COURSE_MODULE.md
```

### Tech Stack

**Backend:**
- Django 5.1.4 (Python web framework)
- SQLite (local development)
- PostgreSQL (production on Azure)

**APIs:**
- U.S. Census Bureau API (free demographics)
- OpenAI GPT-4 (AI content generation)
- (Future) Google Places, Yelp, Parks API, etc.

**Frontend (To Be Built):**
- HTML5, CSS3, JavaScript
- Tailwind CSS or Bootstrap (TBD)
- Responsive design (mobile-first)

**Deployment:**
- Azure App Service (Django hosting)
- Azure Database for PostgreSQL
- Azure Storage (static files, media)
- Azure Functions (scheduled tasks)

**Analytics:**
- Google Analytics 4 (traffic tracking)
- ContentPerformance model (daily snapshots)
- Power BI (business intelligence)

---

## 🚨 Important Notes

### Articles Start UNPUBLISHED

**Why?**
AI is good but not perfect. Always review before publishing:
- ✅ Check factual accuracy (verify Census numbers)
- ✅ Verify data citations (link to sources)
- ✅ Ensure appropriate tone (friendly, welcoming)
- ✅ Fix any AI "hallucinations" (made-up facts)
- ✅ Add SEO meta description and keywords

**How to Publish:**
1. Go to http://localhost:8002/admin/core/article/
2. Click article to edit
3. Review content carefully
4. Check "Published" checkbox
5. Set "Published date" to today
6. Save

### Cost Management

**Census API:** FREE (no limit)

**OpenAI GPT-4:**
- $0.03 per 1K input tokens
- $0.06 per 1K output tokens
- Average article: ~3,000 tokens total
- **Cost: ~$0.15 per article**

**Budget Example:**
- 24 Springfields × $0.15 = $3.60 (one-time)
- 228 cities × $0.15 = $34.20 (full portfolio)
- 228 cities × 30 articles × $0.15 = $1,026 (full content library)

**Pro Tip:** Use `--dry-run` to preview before spending money!

### Data Accuracy

**Census Data:**
- Source: U.S. Census Bureau (official government data)
- Dataset: American Community Survey 5-Year Estimates (2022)
- Update Frequency: Annually (every October)
- Accuracy: ±5% margin of error for small cities

**AI-Generated Content:**
- Model: GPT-4 (most accurate as of 2026)
- Incorporates: Real Census data from our database
- Caution: May "hallucinate" details not in prompt
- **Always fact-check before publishing!**

---

## 📞 Support

### Get Help

**Email:** gregory.woodruff@cloudandsecurelimited.com

**GitHub:** github.com/cloudandsecurelimited/missouriconstruction

**Course Forum:** youbetyourazure.com/community

**Office Hours:** Wednesdays 2-4 PM CST

### Hire Us

**Custom Implementation:** $5,000+
- We build your multi-site platform
- Configure AI content generation
- Create Power BI dashboards
- Train your team
- 6 months support

**Consulting Retainer:** $2,000/month
- 8 hours monthly consultation
- Priority email support
- Code review & optimization
- Quarterly strategy sessions

**Partnership Program:**
- You bring clients, we build + split revenue 60/40
- Technical expertise provided
- Sales/marketing your responsibility
- Recurring subscription profits shared

**Contact:** sales@cloudandsecurelimited.com

---

## 📄 License

**MIT License** - Use commercially, modify freely, teach others.

**Attribution:** Link back to youbetyourazure.com

**Support:** Hire us for consulting or send students our way!

---

**Built by:** Gregory Woodruff  
**Company:** Cloud and Secure Limited  
**Course:** youbetyourazure.com  
**Updated:** February 2026  
**Version:** 1.0
