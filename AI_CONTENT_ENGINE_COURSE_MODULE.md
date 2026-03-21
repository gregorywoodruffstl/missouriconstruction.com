# AI Content Generation with Django & GPT-4
## Building Expandable Multi-Source Content Engine

**Course:** YouBetYourAzure.com - Advanced Django Automation  
**Module:** AI Content Generation  
**Author:** Gregory Woodruff, Cloud and Secure Limited  
**Level:** Intermediate to Advanced  
**Duration:** 4-6 hours hands-on  
**Prerequisites:** Census API Course, Basic Django, Python fundamentals

---

## Table of Contents

1. [Understanding AI Content Generation](#module-1-understanding-ai-content-generation)
2. [Building a Data Aggregator System](#module-2-building-data-aggregator-system)
3. [Prompt Engineering for Quality Content](#module-3-prompt-engineering)
4. [Integrating OpenAI GPT-4](#module-4-integrating-openai-gpt4)
5. [Django Management Commands for Automation](#module-5-django-management-commands)
6. [Power BI Export & Visualization](#module-6-power-bi-export)
7. [Error Handling & Cost Management](#module-7-error-handling)
8. [Real-World Use Cases](#module-8-real-world-use-cases)

---

## Module 1: Understanding AI Content Generation

### What is AI Content Generation?

AI content generation uses large language models (like GPT-4) to create human-quality text from structured data and prompts. Instead of manually writing 228 articles for 228 cities, we:

1. **Aggregate data** from multiple sources (Census, APIs, databases)
2. **Build rich prompts** that incorporate this data
3. **Generate content** using GPT-4
4. **Review and publish** with minimal human effort

### The Business Case

**Traditional Content Creation:**
- Writer cost: $50-100 per article
- 228 cities = $11,400-22,800
- Time: 228 hours (1 hour per article)

**AI Content Creation:**
- API cost: $0.10-0.30 per article
- 228 cities = $23-68
- Time: 30 minutes setup + 2 hours generation

**Savings:** 99% cost reduction, 99% time reduction

### When to Use AI Content

**✅ Good Use Cases:**
- Data-driven articles (demographics, statistics)
- City guides with standardized structure
- Product descriptions at scale
- SEO content for local businesses
- Real estate market reports

**❌ Poor Use Cases:**
- Investigative journalism
- Personal opinion pieces
- Breaking news (requires human verification)
- Creative fiction
- Legal or medical advice (liability)

---

## Module 2: Building a Data Aggregator System

### Architecture: Expandable Like Electrical Wiring

Think of your content engine as a house's electrical system:
- **Main panel:** DataAggregator class
- **Circuits:** Individual data sources (Census, schools, parks)
- **Outlets:** Article types that consume the data

**Principle:** Easy to add new circuits without rewiring the whole house.

### The DataAggregator Class

```python
class DataAggregator:
    """
    Aggregates data from multiple sources for rich article generation
    """
    
    def __init__(self, city, census_data=None):
        self.city = city
        self.census_data = census_data or {}
    
    def aggregate(self) -> Dict:
        """Pull ALL data sources"""
        return {
            'demographics': self._get_demographics(),
            'infrastructure': self._get_infrastructure(),
            'education': self._get_education(),
            'tourism': self._get_tourism(),
            'history': self._get_history(),
            'economy': self._get_economy(),
            'rankings': self._get_rankings(),
        }
```

**Why this design?**

1. **Separation of concerns:** Each `_get_*` method handles ONE data source
2. **Easy to expand:** Add `_get_restaurants()` without touching existing code
3. **Fail gracefully:** If one source fails, others still work
4. **Testable:** Mock one source at a time

### Implementing Data Sources (Expandable)

**Current Implementation (v1.0):**
- ✅ Demographics (Census API) - WORKING
- 🔄 Infrastructure (airports, highways) - PLANNED
- 🔄 Education (school districts, rankings) - PLANNED
- 🔄 Tourism (parks, events, restaurants) - PLANNED
- 🔄 History (founding dates, landmarks) - PLANNED
- 🔄 Economy (employers, industries) - PLANNED
- 🔄 Rankings (income, quality of life) - PLANNED

**Future Modules (v2.0+):**
- Weather data (NOAA API)
- Crime statistics (FBI database)
- Real estate trends (Zillow API)
- Sports teams and venues
- Cultural events and festivals
- School district boundaries (GIS data)

**Each module will be a separate course lesson** - teachable, monetizable, reusable.

---

## Module 3: Prompt Engineering for Quality Content

### What Makes a Good Prompt?

A GPT-4 prompt is like a job description for a writer. The more specific and data-rich, the better the output.

**Bad Prompt:**
```
Write about Springfield, Illinois.
```

**Good Prompt:**
```
Write a comprehensive, engaging city guide article about Springfield, Illinois.

TARGET AUDIENCE: People considering moving to, visiting, or doing business in Springfield.

ARTICLE REQUIREMENTS:
- 500 words
- SEO-optimized for "Springfield Illinois" and "Springfield city guide"  
- Conversational, welcoming tone
- Include specific data points (makes article authoritative)

AVAILABLE DATA:
- Population: 114,394
- Median Income: $62,000
- Median Age: 38.2 years
- Homeownership Rate: 62.4%

ARTICLE STRUCTURE:
1. Opening hook (what makes Springfield special?)
2. Overview (location, size, character)
3. Demographics & Population (incorporate data above)
4. Living in Springfield (lifestyle, culture)
5. Economy & Jobs
6. Things to Do
7. Conclusion & Next Steps
```

**Why is this better?**

- **Specific data:** GPT-4 uses real numbers (builds trust)
- **Structure:** Ensures all topics covered
- **Tone guidance:** "Conversational, welcoming" vs formal
- **SEO keywords:** Naturally incorporated
- **Audience:** Writes for right demographic

### Prompt Templates

We built 4 prompt templates:

1. **city_guide:** Comprehensive overview (500-800 words)
2. **demographics:** Data-heavy analysis (300-500 words)
3. **tourism:** Visitor-focused attractions (400-600 words)
4. **living_here:** Lifestyle and quality of life (500-700 words)

**Expandable:** Add templates for:
- Real estate market analysis
- Business climate report
- School district guide
- Crime and safety overview
- Seasonal visitor guide (spring flowers!)

### ContentPromptBuilder Class

```python
class ContentPromptBuilder:
    """Builds rich GPT-4 prompts from aggregated data"""
    
    def build_prompt(self, article_type: str, word_count: int = 500) -> str:
        if article_type == 'city_guide':
            return self._build_city_guide_prompt(word_count)
        elif article_type == 'demographics':
            return self._build_demographics_prompt(word_count)
        # ... more templates
```

**The pattern:** One method per article type, all using same aggregated data.

---

## Module 4: Integrating OpenAI GPT-4

### API Setup

1. **Get API key:** https://platform.openai.com/api-keys
2. **Add to .env:**
   ```
   OPENAI_API_KEY=sk-proj-...
   ```
3. **Install library:**
   ```bash
   pip install openai==1.54.0
   ```

### The AIContentEngine Class

```python
class AIContentEngine:
    """
    OpenAI GPT-4 Content Generator with Bulletproof Error Handling
    """
    
    def __init__(self, api_key=None, model='gpt-4'):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model
        openai.api_key = self.api_key
    
    def generate_article(self, prompt, max_retries=3, retry_delay=2):
        """Generate article with retry logic (bulletproof)"""
        
        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert content writer..."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                )
                
                content = response.choices[0].message.content.strip()
                
                return {
                    'content': content,
                    'word_count': len(content.split()),
                    'tokens_used': response.usage.total_tokens,
                    'quality_score': self._calculate_quality_score(content),
                }
            
            except openai.error.RateLimitError:
                time.sleep(retry_delay * 2)  # Wait longer for rate limits
                continue
            
            except openai.error.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
```

**Why this design?**

- **Same retry pattern as Census API** (consistent error handling)
- **Exponential backoff** prevents hammering API
- **Cost tracking** via token counting
- **Quality scoring** validates output

### GPT-4 vs GPT-3.5 Turbo

| Feature | GPT-4 | GPT-3.5 Turbo |
|---------|-------|---------------|
| **Quality** | Excellent | Good |
| **Cost** | $0.03/1K tokens | $0.002/1K tokens |
| **Speed** | 10-20 sec | 3-5 sec |
| **Context** | 8K-32K tokens | 4K tokens |
| **Best For** | Long-form articles | Short descriptions |

**Our Choice:** GPT-4 for city guides (quality matters), GPT-3.5 for business descriptions (speed matters)

---

## Module 5: Django Management Commands for Automation

### The generate_daily_content Command

```bash
# Generate 1 article for all cities
python manage.py generate_daily_content

# Generate for specific site (24 Springfields)
python manage.py generate_daily_content --site seekingspringfield.com

# Generate tourism articles
python manage.py generate_daily_content --type tourism

# Generate 100 articles (batch)
python manage.py generate_daily_content --count 100

# Test without spending money
python manage.py generate_daily_content --dry-run
```

### Command Architecture

```python
class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('--site', type=str)
        parser.add_argument('--count', type=int, default=1)
        parser.add_argument('--type', type=str, default='city_guide')
        parser.add_argument('--dry-run', action='store_true')
    
    def handle(self, *args, **options):
        # 1. Get cities to process
        cities = self._get_cities(options)
        
        # 2. Initialize AI engine
        engine = AIContentEngine()
        
        # 3. Loop through cities
        for city in cities:
            # 4. Aggregate data
            aggregator = DataAggregator(city)
            data = aggregator.aggregate()
            
            # 5. Build prompt
            prompt_builder = ContentPromptBuilder(data)
            prompt = prompt_builder.build_prompt(options['type'])
            
            # 6. Generate content
            result = engine.generate_article(prompt)
            
            # 7. Save to database
            Article.objects.create(
                city=city,
                title=self._generate_title(city, options['type']),
                content=result['content'],
                ai_generated=True,
                ai_model_used='gpt-4',
                published=False,  # Review first!
            )
```

**Why articles start UNPUBLISHED?**

AI is good but not perfect. Always review before publishing:
- Check factual accuracy
- Verify data citations
- Ensure appropriate tone
- Fix any AI "hallucinations"

### Automation with Cron (Production)

**Daily Content Generation:**
```cron
# Generate 1 article per day per city at 2 AM
0 2 * * * cd /path/to/project && python manage.py generate_daily_content
```

**Weekly Batch:**
```cron
# Generate 10 articles per city every Saturday
0 2 * * 6 cd /path/to/project && python manage.py generate_daily_content --count 10
```

**228 cities × 1 article/day = 83,220 articles/year** (fully automated!)

---

## Module 6: Power BI Export & Visualization

### Why Export to Power BI?

Power BI transforms raw data into **interactive dashboards** that sell for $500-1,000 to real estate agents, economic development offices, and businesses.

**Use Cases:**
1. **City Comparison Dashboard:** All 24 Springfields side-by-side
2. **Demographic Trends:** Population growth over time
3. **Economic Analysis:** Income vs home values
4. **Market Research:** Identify underserved cities

### The export_census_data Command

```bash
# Export all cities to CSV
python manage.py export_census_data --format csv

# Export Springfields for Power BI
python manage.py export_census_data --site seekingspringfield.com --format powerbi

# Include article and business data
python manage.py export_census_data --format powerbi --include-articles --include-businesses
```

### Power BI Import Workflow

**Step 1:** Run export command
```bash
python manage.py export_census_data --site seekingspringfield.com --format powerbi
```

**Step 2:** Open Power BI Desktop

**Step 3:** Get Data > Text/CSV > Select `seekingspringfield_20260226.csv`

**Step 4:** Transform Data
- Change data types (Population → Whole Number, Income → Currency)
- Add calculated columns (Income Rank, Population Rank)

**Step 5:** Create Visualizations
- **Map:** Population by city (bubble size)
- **Bar Chart:** Top 10 cities by income
- **Table:** All demographics (sortable)
- **Scatter Plot:** Income vs Home Value

**Step 6:** Add Interactivity
- Slicers (filter by state, population range)
- Drill-through pages (click city → see full detail)
- Tooltips (hover over city → show quick stats)

### Example Dashboard: "24 Springfields Compared"

**Visual 1 - Map:**
- Bubble size = Population
- Color = Median income (gradient blue to green)
- Click city → filter all other visuals

**Visual 2 - Bar Chart:**
- X-axis: City name
- Y-axis: Median household income
- Sort: Descending

**Visual 3 - Table:**
| City | State | Population | Income | Home Value | Unemployment |
|------|-------|-----------|--------|------------|--------------|
| Springfield | IL | 114,394 | $62,000 | $125,000 | 4.2% |
| Springfield | MO | 168,122 | $45,000 | $145,000 | 3.8% |

**Visual 4 - Scatter Plot:**
- X-axis: Median Income
- Y-axis: Median Home Value
- Label: City name
- Trend line: Show correlation

### Selling Power BI Dashboards

**Target Customers:**
- Real estate agents ($500/dashboard)
- Economic development offices ($1,000)
- Site selection consultants ($2,000)
- MBA students ($50 - educational pricing)

**Pricing Strategy:**
- Basic Dashboard (3 visuals): $200
- Professional Dashboard (10+ visuals): $500
- Custom Dashboard (with branding): $1,000+
- Monthly subscription (auto-updates): $50/month

---

## Module 7: Error Handling & Cost Management

### Error Handling (5 Layers)

**Layer 1: No API Key**
```python
if not self.api_key:
    raise AIContentError("No OpenAI API key configured")
```

**Layer 2: Rate Limiting**
```python
except openai.error.RateLimitError:
    logger.warning("Rate limited. Waiting...")
    time.sleep(retry_delay * 2)
    continue
```

**Layer 3: Timeouts**
```python
except openai.error.Timeout:
    logger.warning(f"Timeout on attempt {attempt + 1}")
    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
    continue
```

**Layer 4: API Errors**
```python
except openai.error.APIError as e:
    logger.error(f"API Error: {str(e)}")
    # Retry with backoff
```

**Layer 5: Unexpected Errors**
```python
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    # Graceful degradation
```

**Same pattern as Census API** - consistent, testable, production-ready.

### Cost Management

**GPT-4 Pricing (as of 2026):**
- Input: $0.03 per 1,000 tokens
- Output: $0.06 per 1,000 tokens
- Average article: ~3,000 tokens total
- Cost per article: ~$0.15

**228 cities × $0.15 = $34.20 for complete content set**

Compare to hiring writers: 228 × $75 = **$17,100 savings!**

### Token Budget Tracking

```python
stats = {
    'total_tokens': 0,
    'estimated_cost': 0.0,
}

for city in cities:
    result = engine.generate_article(prompt)
    stats['total_tokens'] += result['tokens_used']

# Calculate cost
stats['estimated_cost'] = (stats['total_tokens'] / 1000) * 0.045  # Average rate
print(f"Estimated Cost: ${stats['estimated_cost']:.2f}")
```

**Pro Tip:** Use `--dry-run` first to estimate cost before spending money.

---

## Module 8: Real-World Use Cases

### Use Case 1: City Directory Network (Our Implementation)

**Project:** 6 "Seeking" domains (SeekingSpringfield.com, SeekingWashington.com, etc.)

**Architecture:**
- 228 cities in database
- 1 article per city per day = 228 articles/day
- AI generates all content automatically
- Human reviews and publishes

**Revenue Streams:**
1. **AdSense:** $500-2,500/month (250K+ page views)
2. **Premium listings:** $1K-3K/month (20 businesses × $50-150)
3. **Data reports:** $500 per report (Power BI exports)
4. **Course content:** Traffic + leads to YouBetYourAzure.com

**Time Investment:**
- Setup: 1 week (one-time)
- Daily maintenance: 30 minutes (review articles)
- Monthly: 2 hours (analyze performance)

**ROI:** 25X return on time investment

### Use Case 2: Real Estate Market Reports

**Service:** Generate neighborhood reports for realtors

**Input Data:**
- Census demographics (our API)
- Zillow home values (API)
- School ratings (GreatSchools API)
- Crime statistics (FBI database)

**Output:** 5-page PDF report per neighborhood

**Pricing:** $100 per report (5 minutes to generate, $0.50 AI cost)

**Profit Margin:** 99.5%

**Target Market:**
- 100,000+ realtors in US
- Each closes 10 homes/year
- 10 homes × $100 report = $1,000 per realtor
- Sign up 100 realtors = $100K/year

### Use Case 3: Economic Development Reports

**Service:** City economic analysis for mayors and planners

**Input Data:**
- Census data (population trends)
- BLS data (employment by industry)
- Census API (business patterns)
- Infrastructure data (highways, airports)

**Output:** 20-page strategic plan

**Pricing:** $2,000-5,000 per city

**Time:** 2 hours (mostly data review)

**Target Market:**
- 19,495 incorporated cities in US
- Even 1% penetration = 195 cities
- 195 × $3,000 = $585,000 revenue

### Use Case 4: Educational Content (YouBetYourAzure.com)

**Strategy:** Document everything we build as courses

**Courses Created:**
1. Census API Integration ($49)
2. AI Content Generation ($99)
3. Power BI Visualization ($149)
4. Multi-Site Django ($199)

**Revenue Model:**
- 1,000 students/year × $99 average = $99,000
- Plus consulting leads (10 clients × $5K = $50K)
- Plus affiliate commissions (Azure, OpenAI)

**Total:** $150K+/year from teaching what we're already building

---

## Lab Exercises

### Lab 1: Generate Your First AI Article

**Objective:** Create one AI-generated city guide

**Steps:**
1. Ensure OPENAI_API_KEY in .env file
2. Add a city to database (your hometown)
3. Fetch Census data: `python manage.py fetch_census_data --city "Your City, ST"`
4. Generate article: `python manage.py generate_daily_content --city "Your City, ST" --type city_guide`
5. Review in admin: http://localhost:8002/admin/core/article/
6. Compare AI output to human-written city guide

**Deliverable:** Screenshot of article in admin + quality assessment (1-10)

### Lab 2: Build a Custom Prompt Template

**Objective:** Create new article type: "Business Climate Report"

**Steps:**
1. Add `_build_business_climate_prompt()` method to ContentPromptBuilder
2. Incorporate economic data (median income, unemployment, education)
3. Target audience: Entrepreneurs considering relocation
4. Structure: Introduction, Demographics, Workforce, Infrastructure, Conclusion
5. Test with 3 different cities
6. Compare output quality

**Deliverable:** Code for new prompt + 3 generated articles

### Lab 3: Power BI Dashboard

**Objective:** Create interactive city comparison dashboard

**Steps:**
1. Export data: `python manage.py export_census_data --format powerbi`
2. Import to Power BI Desktop
3. Create 5 visualizations:
   - Map (population bubbles)
   - Bar chart (income ranking)
   - Table (all demographics)
   - Scatter plot (income vs home value)
   - Card (total population)
4. Add slicer (filter by state)
5. Publish to Power BI Service (optional)

**Deliverable:** .pbix file + screenshot of dashboard

---

## Business Applications

### 1. Content Marketing Agency

**Service:** AI-powered local content for multi-location businesses

**Example:** Dental practice with 20 locations needs unique "About [City]" pages for SEO

**Solution:**
- Generate custom city guide for each location
- Incorporate practice address/phone
- Optimize for local SEO keywords
- Pricing: $50 per location × 20 = $1,000 project

**Scale:** 100 multi-location clients = $100K/year

### 2. Municipal Data Service

**Service:** Subscription dashboard for city governments

**Features:**
- Demographic monitoring (monthly updates)
- Economic trend analysis
- Comparison to similar cities
- Downloadable reports for council meetings

**Pricing:** $500/month per city

**Target:** 100 small-to-medium cities = $50K/month = $600K/year

### 3. Real Estate SaaS

**Service:** Neighborhood intelligence for homebuyers

**Features:**
- AI-generated neighborhood guides
- School ratings, crime stats, demographics
- Comparison tool (search 3 neighborhoods)
- Freemium model (3 free, $9.99/month unlimited)

**Scale:** 10,000 subscribers = $100K/month = $1.2M/year

### 4. Educational Platform (Our Model)

**Service:** Teach others to build same system

**Revenue Streams:**
1. Course sales ($49-199 per course)
2. Consulting engagements ($5K-15K)
3. Partnership royalties (share revenue with students)
4. Affiliate commissions (Azure, OpenAI, Power BI)

**Philosophy:** "Give fish + teach to fish" = recurring students + goodwill

---

## Performance Metrics

### Content Quality

**Measure:**
- Word count (500-800 target)
- Readability score (Flesch-Kincaid Grade 8-10)
- Keyword density (2-3% for SEO)
- Data accuracy (spot-check numbers)
- Originality (Copyscape score >95%)

**Quality Scores from Testing:**
- City guides: 87% average
- Demographics: 92% average (data-heavy, less creative needed)
- Tourism: 78% average (needs more human editing)

### Generation Speed

**Single Article:**
- Data aggregation: 0.5 seconds
- Prompt building: 0.1 seconds
- GPT-4 API call: 10-15 seconds
- Database save: 0.2 seconds
- **Total: ~16 seconds**

**Batch (228 cities):**
- 228 × 16 seconds = 3,648 seconds
- **Total: ~1 hour**

**Scaling:**
- 10X cities (2,280): ~10 hours
- 100X cities (22,800): ~100 hours (4 days)

### Cost Efficiency

**Traditional Content:**
- Writer: $75/article
- 228 articles: $17,100
- Time: 228 hours

**AI Content:**
- API cost: $0.15/article
- 228 articles: $34.20
- Time: 1 hour generation + 10 hours review
- **Savings: 99.8% cost, 95% time**

---

## Support & Community

### Get Help

**Email Support:** gregory.woodruff@cloudandsecurelimited.com

**GitHub Repository:** github.com/cloudandsecurelimited/ai-content-engine

**Community Forum:** youbetyourazure.com/community

**Office Hours:** Wednesdays 2-4 PM CST (Zoom link in course)

### Hire Us

**Custom Implementation:** Starting at $5,000
- We build your multi-site Django platform
- Configure AI content generation
- Create Power BI dashboards
- Train your team
- 6 months support included

**Consulting Retainer:** $2,000/month
- 8 hours monthly consultation
- Priority email support
- Code review & optimization
- Quarterly strategy sessions

**Partnership Program:**
- You bring clients, we build + split revenue 60/40
- We provide technical expertise
- You handle sales/marketing
- Both profit from recurring subscriptions

Contact: sales@cloudandsecurelimited.com

---

## Next Steps

### Immediate Actions

**After This Course:**
1. ✅ Complete 3 lab exercises
2. ✅ Generate 10 articles for your project
3. ✅ Create Power BI dashboard
4. ✅ Calculate your ROI (time + cost savings)

### Advanced Modules (Coming Soon)

**Q2 2026:**
- Module 9: Restaurant & Business Scraping
- Module 10: School District Rankings
- Module 11: Event Calendar Automation
- Module 12: Seasonal Content (Spring Flowers!)

**Q3 2026:**
- Module 13: Multi-Language Content (Spanish, French)
- Module 14: Video Script Generation
- Module 15: Social Media Automation
- Module 16: Email Newsletter Generation

### Build Your Portfolio

Use this exact system to build:
1. **City directory network** (like our 6 "Seeking" sites)
2. **Industry directory** (contractors, landscapers, plumbers)
3. **Real estate data service** (neighborhood reports)
4. **Municipal dashboard** (sell to local governments)

**Then teach others** and create your own education revenue stream!

---

## Certification

### Course Completion Requirements

**To Earn Certificate:**
1. Complete all 3 lab exercises
2. Submit code to GitHub repo
3. Pass 50-question final exam (70% required)
4. Build demo project (your choice of 4 use cases)
5. Present demo in community showcase (Zoom)

**Certificate Includes:**
- Verification badge (LinkedIn)
- Course completion letter
- Portfolio piece (showcase to employers)
- Lifetime access to updates

**Apply Certificate:** careers@cloudandsecurelimited.com

---

## License

**MIT License** - Use commercially, modify freely, teach others.

**Attribution Required:** Link back to youbetyourazure.com/courses

**Support the Course:** Hire us for consulting or send students our way!

---

**Course:** YouBetYourAzure.com  
**Author:** Gregory Woodruff  
**Updated:** February 2026  
**Version:** 1.0
