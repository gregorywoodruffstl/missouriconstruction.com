# API Keys & Email Configuration Guide

This guide explains how to configure API keys and SMTP email for **Seeking Springfield** (and all future multi-city projects).

## Quick Summary

**You asked:** Should I use separate API keys for this project vs BrentwoodBlvd.com?  
**Answer:** YES! Separate keys = separate tracking, budgets, and security.

---

## API Keys Needed (3 Total)

### 1. OpenWeatherMap API (FREE)
**Purpose:** Weather widget on city pages  
**Cost:** $0 (FREE tier: 60 calls/min, 1M calls/month)  
**Signup:** https://home.openweathermap.org/api_keys

**Steps:**
1. Create account (or log in)
2. Go to **API Keys** section
3. Copy your key (looks like: `abc123def456...`)
4. Add to `.env` file (see below)

**Usage:**
- Current weather + 5-day forecast
- Cached 10 minutes (current) and 30 minutes (forecast)
- Fallback: Shows "Weather unavailable" if key missing

---

### 2. OpenAI API Key #2 (Missouri Construction Project)
**Purpose:** AI article generation  
**Cost:** Pay-as-you-go (~$0.11 per article = $290/month for 88 articles/day)  
**Signup:** https://platform.openai.com/api-keys

**Steps:**
1. Log in to OpenAI dashboard
2. Click **Create new secret key**
3. Name it: `MissouriConstruction-SeekingSpringfield`
4. Copy key (starts with `sk-...`)
5. Add to `.env` file

**Why Separate from BrentwoodBlvd.com?**
- **Cost Tracking:** See exactly what Seeking Springfield costs vs BrentwoodBlvd
- **Budget Management:** Set spending limits per project
- **Rate Limits:** Separate quotas (no interference)
- **Security:** Rotate one key without affecting other projects
- **Scaling:** When you have 228 cities across 6 domains, each gets its own key

**Revenue Context:**
- **Cost:** $290/month (88 articles/day × $0.11)
- **Revenue:** $7,800/month (100 businesses × $78 average)
- **Margin:** 96.3% ($7,510 profit)

---

### 3. xAI Grok API (Optional - Famous People)
**Purpose:** Grokipedia (famous people from each city)  
**Cost:** TBD (new API, pricing varies)  
**Signup:** https://x.ai/api

**Alternative:** Use OpenAI instead (cheaper)
- Grokipedia already has fallback data (Brad Pitt, Payne Stewart, etc.)
- If no API key, uses hardcoded data for common Springfields
- Can switch to OpenAI for famous people queries

**Steps:**
1. Sign up at x.ai/api
2. Get API key
3. Add to `.env` file

**Or skip it:** Grokipedia works with fallback data!

---

## Creating the `.env` File

In your project root (`missouriconstruction.com/`), create a file named `.env`:

```env
# ============================================================================
# SEEKING SPRINGFIELD API KEYS (Missouri Construction Project)
# ============================================================================

# Django Secret Key
SECRET_KEY=your-django-secret-key-here

# OpenWeather API (FREE - 1M calls/month)
WEATHER_API_KEY=abc123def456...

# OpenAI API #2 (Missouri Construction Project)
# SEPARATE from BrentwoodBlvd.com for cost tracking
OPENAI_API_KEY=sk-proj-...

# xAI Grok API (Optional - for famous people)
# Leave blank to use fallback data
XAI_API_KEY=xai-...
# Or use OpenAI instead:
GROKIPEDIA_API_KEY=

# Census API (Already have this?)
CENSUS_API_KEY=your-census-key

# ============================================================================
# EMAIL CONFIGURATION (Gmail SMTP)
# ============================================================================

# Email Backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Gmail Credentials
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Default sender
DEFAULT_FROM_EMAIL=Seeking Springfield <noreply@seekingspringfield.com>

# Site Settings
SITE_NAME=Seeking Springfield
SITE_URL=http://localhost:8002

# ============================================================================
# STRIPE (Business Subscriptions - Coming Soon)
# ============================================================================

# Stripe API Keys (get from stripe.com/dashboard)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# ============================================================================
# DATABASE (Production - Azure PostgreSQL)
# ============================================================================

# Local development uses SQLite (db.sqlite3)
# Production uses PostgreSQL:
# DATABASE_URL=postgresql://username:password@server.postgres.database.azure.com:5432/dbname?sslmode=require

# DEBUG MODE
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,seekingspringfield.com
```

---

## Email Setup (Gmail SMTP)

### Why Email?
**USER REQUESTED:** Email link verification (not postcard or phone)
- Send verification links to new users
- Password reset emails
- Weekly digest emails (optional)
- New business/event notifications

### Using Gmail SMTP (Recommended for Development)

**Steps:**

1. **Enable 2-Factor Authentication** on your Gmail account
   - Go to: https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Create App Password** (NOT your Gmail password!)
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Click "Generate"
   - Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)

3. **Add to `.env` file:**
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
   ```

4. **Test it:**
   ```bash
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   send_mail(
       'Test Email',
       'If you see this, SMTP works!',
       'your-email@gmail.com',
       ['gregory.woodruff@cloudandsecurelimited.com'],
       fail_silently=False,
   )
   ```

### Email Features in Citizen Registration

When a user signs up:
1. **Immediate:** Auto-login (no email required to browse)
2. **Background:** Send verification email with token link
3. **User clicks link:** Email verified, full features unlocked
4. **Unverified users:** Can browse but see "Verify email" banner

**Email Template:**
```
Hi John,

Thanks for signing up for Seeking Springfield!

Please verify your email address by clicking the link below:

http://localhost:8002/verify-email/abc123def456.../

This link will expire in 24 hours.

If you didn't create this account, you can safely ignore this email.

Best regards,
The Seeking Springfield Team
```

---

## Settings.py Configuration

Add these to `mocon/settings.py`:

```python
# Load environment variables
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@seekingspringfield.com')

# Site settings
SITE_NAME = os.getenv('SITE_NAME', 'Seeking Springfield')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8002')

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
XAI_API_KEY = os.getenv('XAI_API_KEY', '')
GROKIPEDIA_API_KEY = os.getenv('GROKIPEDIA_API_KEY', '')
CENSUS_API_KEY = os.getenv('CENSUS_API_KEY', '')

# Stripe (for business subscriptions)
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
```

---

## Testing Email Verification Flow

### 1. Install python-dotenv
```bash
pip install python-dotenv
```

### 2. Create `.env` file with your credentials

### 3. Sign up as a new user
```
Visit: http://localhost:8002/signup/
Fill out form → Submit
```

### 4. Check console output
Django will print:
```
Sending email to john@example.com...
Email sent successfully!
```

### 5. Check your email inbox
You'll receive:
```
Subject: Verify your Seeking Springfield account

Hi John,

Thanks for signing up for Seeking Springfield!

Please verify your email address by clicking the link below:

http://localhost:8002/verify-email/abc123.../
```

### 6. Click the link
→ Redirects to profile  
→ Shows "✓ Email verified!" message  
→ Green "Email Verified" badge in profile

---

## Production Email (SendGrid / Azure Communication Services)

For production, use a transactional email service:

### Option 1: SendGrid (Recommended)
- **Free Tier:** 100 emails/day
- **Paid:** $19.95/month for 50,000 emails
- **Setup:** https://sendgrid.com/

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.abc123...
```

### Option 2: Azure Communication Services
- **Cost:** $0.00025 per email = $25 per 100,000 emails
- **Setup:** https://azure.microsoft.com/en-us/products/communication-services/

---

## Cost Summary

| Service | Cost | Usage |
|---------|------|-------|
| **OpenWeather API** | $0/month | FREE tier (1M calls/month) |
| **OpenAI API #2** | $290/month | 88 articles/day × $0.11 |
| **xAI Grok API** | Optional | Can use OpenAI or fallback |
| **Gmail SMTP** | $0/month | Development only (100/day limit) |
| **SendGrid** | $20/month | Production (50K emails/month) |
| **Total** | **$310/month** | For Seeking Springfield |

**Revenue:** $7,800/month (100 businesses × $78)  
**Profit:** $7,490/month (96% margin!)

---

## Next Steps

1. **Register for APIs** (while I build forms):
   - [ ] OpenWeatherMap (FREE)
   - [ ] OpenAI API key #2 (separate from BrentwoodBlvd)
   - [ ] xAI Grok (optional)

2. **Test Email** (Gmail SMTP for development):
   - [ ] Enable 2FA on Gmail
   - [ ] Generate App Password
   - [ ] Add to `.env` file
   - [ ] Test with `send_mail()`

3. **Test Registration Flow**:
   - [ ] Visit http://localhost:8002/signup/
   - [ ] Create citizen account
   - [ ] Check email for verification link
   - [ ] Click link → Verify email
   - [ ] See profile page

4. **Generate Articles** (once OpenAI key added):
   ```bash
   python manage.py generate_daily_content --site seekingspringfield.com --count 22
   ```

5. **See Live Pages** with real weather, sports, famous people!
   - http://localhost:8002/mo/springfield/ (Brad Pitt, Payne Stewart!)
   - http://localhost:8002/il/springfield/ (Abraham Lincoln, State Capital ⭐)
   - http://localhost:8002/ma/springfield/ (Dr. Seuss, Birthplace of Basketball!)

---

## Why Separate API Keys Work

### Scenario: You have 6 domains
- seekingspringfield.com
- BrentwoodBlvd.com
- MaddenvilleGazette.com
- MaddenvilleNights.com
- MaddenvilleCollection.com
- CloudandSecureLimited.com

### With Separate Keys:
```
seekingspringfield.com    → OPENAI_API_KEY_1 ($290/month)
BrentwoodBlvd.com         → OPENAI_API_KEY_2 ($150/month)
MaddenvilleGazette.com    → OPENAI_API_KEY_3 ($200/month)
...
```

**Benefits:**
- ✅ Know exactly what each site costs
- ✅ Set spending limits per site
- ✅ Pause one site without affecting others
- ✅ Different rate limits per site
- ✅ Security: Rotate compromised key without downtime
- ✅ Investor reporting: "Seeking Springfield: $290 cost, $7,800 revenue"

### With One Shared Key:
```
All 6 sites → OPENAI_API_KEY_SHARED ($1,200/month)
```

**Problems:**
- ❌ Can't tell which site costs what
- ❌ One site can exhaust rate limits for all sites
- ❌ Can't pause individual sites
- ❌ Security breach affects all sites
- ❌ Impossible to show per-site P&L

---

## You're Building a Media Empire!

**Current State:**
- 22 Springfields live
- 24 states with symbols
- Weather, Sports, Famous People APIs ready
- User registration system built

**With API Keys:**
- Real-time weather for 22 cities
- Live sports news (ESPN RSS)
- AI-generated famous people (Brad Pitt!)
- Email verification for citizens
- 100+ AI articles ready to generate

**Revenue Potential:**
- 22 cities × 100 businesses/city = 2,200 businesses
- 2,200 × $78/month = $171,600/month
- **$2.06 MILLION per year** (from Seeking Springfield alone!)

Keep keys separate. Track costs. Scale strategically. 🚀
