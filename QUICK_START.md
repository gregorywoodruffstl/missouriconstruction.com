# Quick Start Guide - Test the AI Content Engine

## Prerequisites

1. **Census API Key** (FREE)
   - Get at: https://api.census.gov/data/key_signup.html
   - Add to `.env` file: `CENSUS_API_KEY=your-key-here`

2. **OpenAI API Key** (PAID - but cheap!)
   - Get at: https://platform.openai.com/api-keys
   - Add to `.env` file: `OPENAI_API_KEY=sk-proj-your-key-here`
   - Cost: ~$0.15 per article

---

## 5-Minute Test (No Money Spent!)

Test the entire system without spending money using `--dry-run` flags.

### Step 1: Populate Springfield Cities (Dry Run)

```bash
cd "missouriconstruction.com"
python manage.py populate_springfields --dry-run
```

**Expected Output:**
```
================================================================================
POPULATE SPRINGFIELDS
================================================================================

🔍 DRY RUN - Would create/verify site: seekingspringfield.com

📍 Processing 24 Springfield cities...

[1/24] Springfield, IL
   🔍 Would create: Springfield, IL
      Note: State capital, home of Abraham Lincoln
[2/24] Springfield, MO
   🔍 Would create: Springfield, MO
      Note: Birthplace of Route 66
... (22 more)

Total Springfields: 24
Created: 24
```

### Step 2: Fetch Census Data (Dry Run)

```bash
python manage.py fetch_census_data --site seekingspringfield.com --dry-run
```

**Expected Output:**
```
📊 PLAN:
   Cities: 24
   Site Filter: seekingspringfield.com

🔍 DRY RUN MODE - No data will be fetched

[1/24] Springfield, IL
   🔍 Would fetch: Population, Income, Demographics
[2/24] Springfield, MO
   🔍 Would fetch: Population, Income, Demographics
... (22 more)
```

### Step 3: Generate AI Content (Dry Run)

```bash
python manage.py generate_daily_content --site seekingspringfield.com --type city_guide --dry-run
```

**Expected Output:**
```
================================================================================
AI CONTENT GENERATION ENGINE
================================================================================

📊 GENERATION PLAN:
   Cities: 24
   Articles per city: 1
   Article type: city_guide
   Site: seekingspringfield.com
   Mode: DRY RUN

🔍 DRY RUN MODE - No articles will be created

[1/24] Processing: Springfield, Illinois
   📝 Would generate: city_guide article
      Data sources: Census, 7 categories
[2/24] Processing: Springfield, Missouri
   📝 Would generate: city_guide article
... (22 more)

Articles Generated: 24
```

### Step 4: Export Data (Dry Run via Preview)

```bash
# Can't dry-run export, but it's safe (no API calls, just reads database)
# Skip this step in dry-run mode
```

---

## 15-Minute Full Test (Spends ~$0.50)

Now let's run the real thing!

### Step 1: Populate Springfield Cities (REAL)

```bash
python manage.py populate_springfields
```

**Expected Output:**
```
✅ Created site: seekingspringfield.com
✅ Created: Springfield, IL (State capital)
✅ Created: Springfield, MO (Birthplace of Route 66)
... (22 more)

Total: 24 cities created
```

### Step 2: Fetch Census Data (REAL - FREE!)

```bash
python manage.py fetch_census_data --site seekingspringfield.com
```

**Expected Output:**
```
[1/24] Processing: Springfield, Illinois
✅ Population: 114,394 | Median Income: $62,000
[2/24] Processing: Springfield, Missouri
✅ Population: 168,122 | Median Income: $45,000
[3/24] Processing: Springfield, Massachusetts
✅ Population: 155,929 | Median Income: $41,000
... (21 more)

SUMMARY:
Updated: 24
Skipped: 0
Errors: 0
Total Population: 1,234,567
```

**Time:** ~30-45 seconds  
**Cost:** $0 (completely FREE!)

### Step 3: Generate 3 Test Articles (REAL - Costs ~$0.50)

```bash
# Generate 3 articles to test quality before doing all 24
python manage.py generate_daily_content \
  --site seekingspringfield.com \
  --type city_guide \
  --count 3 \
  --city "Springfield, IL"

python manage.py generate_daily_content \
  --site seekingspringfield.com \
  --type tourism \
  --count 1 \
  --city "Springfield, MO"

python manage.py generate_daily_content \
  --site seekingspringfield.com \
  --type demographics \
  --count 1 \
  --city "Springfield, MA"
```

Wait, that's too complex. Let me simplify:

```bash
# Just generate for first 3 cities
# (The command processes in order, so we'll get IL, MO, MA)
# We can't easily limit to first N cities, so comment this strategy out
```

Actually, let's do this differently - generate 1 article, review it, then decide:

```bash
# Generate ONE city guide for Springfield, IL
python manage.py generate_daily_content \
  --site seekingspringfield.com \
  --city "Springfield, IL" \
  --type city_guide
```

**Expected Output:**
```
[1/1] Processing: Springfield, Illinois
🤖 Generating city_guide article...
✅ Generated 587 words (2,341 tokens, Quality: 89%)

SUMMARY:
Articles Generated: 1
Total Words: 587
Total Tokens: 2,341
Estimated Cost: $0.11

⚠️  IMPORTANT: Articles created as UNPUBLISHED
Review in admin: http://localhost:8002/admin/core/article/
```

**Time:** ~15 seconds  
**Cost:** ~$0.11

### Step 4: Review Article in Admin

1. Start server (if not running): `python manage.py runserver 8002`
2. Open browser: http://localhost:8002/admin/
3. Login with your superuser credentials
4. Click **Articles** under CORE section
5. Click the Springfield, IL article
6. **Review the content:**
   - Does it sound natural?
   - Are the Census numbers correct?
   - Is the tone appropriate?
   - Any obvious errors?

**If quality is good,** proceed to generate all 24!

**If quality is poor,** adjust prompts in `core/ai_content_engine.py`

### Step 5: Generate All 24 Springfields (Costs ~$2.64)

```bash
# Generate city guides for all 24 Springfields
python manage.py generate_daily_content \
  --site seekingspringfield.com \
  --type city_guide
```

**Expected Output:**
```
Processing 24 cities...

[1/24] Springfield, IL
✅ Generated 587 words (2,341 tokens, Quality: 89%)

[2/24] Springfield, MO
✅ Generated 612 words (2,453 tokens, Quality: 92%)

... (22 more)

SUMMARY:
Articles Generated: 24
Total Words: 14,208
Total Tokens: 56,832
Estimated Cost: $2.56
```

**Time:** ~6-8 minutes (15 sec per article × 24)  
**Cost:** ~$2.56

### Step 6: Export for Power BI

```bash
python manage.py export_census_data \
  --site seekingspringfield.com \
  --format powerbi \
  --include-articles
```

**Expected Output:**
```
📊 EXPORT PLAN:
   Cities: 24
   Format: POWERBI
   Output: seekingspringfield_20260226.csv

💾 Saved 24 cities to Power BI CSV

✅ Export complete: seekingspringfield_20260226.csv

================================================================================
📊 POWER BI IMPORT INSTRUCTIONS
================================================================================

STEP 1: Open Power BI Desktop

STEP 2: Get Data > Text/CSV
   Select file: seekingspringfield_20260226.csv

STEP 3: Create Visualizations
   📈 SUGGESTED VISUALS:
   - Map: Population by City (bubble size)
   - Bar Chart: Top 10 Cities by Income
   - Table: All Demographics (sortable)
```

**Time:** ~1 second  
**Cost:** $0 (just reads database)

---

## Total Test Cost

**Data Collection (Census API):** **$0** (FREE!)  
**AI Content Generation:** **$2.56** (24 articles)  
**Data Export:** **$0** (FREE!)  

**TOTAL: $2.56** for fully automated content system!

Compare to hiring writers: 24 articles × $75 each = **$1,800**

**Savings: 99.86%**

---

## Next Steps After Testing

### If Everything Works:

1. **Generate more article types:**
   ```bash
   # Tourism articles
   python manage.py generate_daily_content --site seekingspringfield.com --type tourism
   
   # Demographics articles  
   python manage.py generate_daily_content --site seekingspringfield.com --type demographics
   
   # Living here articles
   python manage.py generate_daily_content --site seekingspringfield.com --type living_here
   ```

2. **Publish articles in admin:**
   - Review each article
   - Check "Published" checkbox
   - Set published date
   - Save

3. **Replicate to other sites:**
   ```bash
   # Create commands for other city names
   python manage.py populate_washingtons  # 88 cities
   python manage.py populate_franklins    # 30 cities
   # etc.
   ```

4. **Deploy to Azure:**
   - Follow deployment guide in README.md
   - Switch to PostgreSQL database
   - Set up automated daily content generation
   - Enable Google Analytics

5. **Monetize:**
   - Apply for Google AdSense (need 50+ published articles)
   - Add premium business listings
   - Sell Power BI dashboards ($500 each)
   - Launch YouBetYourAzure courses

### If Something Breaks:

**Error: "No OpenAI API key"**
- Solution: Add `OPENAI_API_KEY=sk-proj-...` to `.env` file
- Verify: `python -c "from decouple import config; print(config('OPENAI_API_KEY'))"`

**Error: "Census API rate limited"**
- Solution: Wait 5 minutes and try again
- Or: Use `--force` flag to continue after errors

**Error: "Article quality too low"**
- Solution: Adjust prompts in `core/ai_content_engine.py`
- Or: Try GPT-4-turbo (faster, cheaper, slightly lower quality)
- Or: Increase `temperature` parameter (more creative)

**Error: "Database locked"**
- Solution: Close other terminal windows running Django
- Or: Delete `db.sqlite3` and run migrations again

---

## Celebrate! 🎉

You just built:
- ✅ Multi-site Django architecture (1 codebase, 6+ sites)
- ✅ Bulletproof Census API integration (with retry logic)
- ✅ AI content engine (GPT-4 generating city guides)
- ✅ Power BI export (visualize demographics)
- ✅ Management commands (automate everything)

**In less than 15 minutes!**

**Next:** Document your learnings in YouBetYourAzure course and teach others!

---

## Questions?

**Email:** gregory.woodruff@cloudandsecurelimited.com  
**Course:** youbetyourazure.com  
**Forum:** youbetyourazure.com/community
