# Missouri Construction — Affiliate Program Reference
# ============================================================================
# HOW THIS WORKS:
# 1. Sign up for each affiliate program below (links provided)
# 2. Get your unique affiliate link / tracking ID from each program
# 3. Paste your link into the [YOUR AFFILIATE LINK] field
# 4. Run: python manage.py seed_affiliates  (already created — updates DB)
# 5. Affiliate links appear on relevant project pages and a dedicated /affiliates/ page
# ============================================================================


## ── TOOLS & EQUIPMENT ───────────────────────────────────────────────────────


### Milwaukee Tool
- **Program:** Impact Radius / ShareASale
- **Sign up:** https://www.milwaukeetool.com/Community/Affiliates
- **Commission:** ~3-5% on tools
- **Why it fits:** Premium contractor-grade tools. Trades audience on this site knows Milwaukee.
- **Placement ideas:** Project pages, gallery pages, apprenticeship page
- [YOUR AFFILIATE LINK]:
- [YOUR TRACKING ID]:


### DeWalt
- **Program:** Impact Radius
- **Sign up:** https://www.dewalt.com/community/affiliates  (or search "DeWalt affiliate program" on Impact)
- **Commission:** ~3-5%
- **Why it fits:** Household name for construction workers. High conversion on tool content.
- **Placement ideas:** Project pages, bids page sidebar
- [YOUR AFFILIATE LINK]:
- [YOUR TRACKING ID]:


### Stanley / Black & Decker
- **Program:** Impact Radius
- **Sign up:** https://www.stanleyblackanddecker.com  (affiliate section)
- **Commission:** ~3-5%
- **Why it fits:** Hand tools, storage, broader trades audience
- **Placement ideas:** Gallery pages, founder story page tool references
- [YOUR AFFILIATE LINK]:
- [YOUR TRACKING ID]:


### Grainger (Safety & PPE)
- **Program:** Direct / CJ Affiliate
- **Sign up:** https://www.grainger.com  → search affiliate or call 1-800-472-4643
- **Commission:** ~2-4%
- **Why it fits:** Safety equipment, PPE, jobsite supplies — every contractor buys from Grainger
- **Placement ideas:** Apprenticeship page, permit/compliance pages
- [YOUR AFFILIATE LINK]:
- [YOUR TRACKING ID]:


## ── SOFTWARE ────────────────────────────────────────────────────────────────


### Autodesk AutoCAD / Construction Cloud
- **Program:** Autodesk Affiliate Program via Impact Radius
- **Sign up:** https://www.autodesk.com/affiliate-program
- **Commission:** Up to 9% on subscriptions
- **Why it fits:** Industry-standard design software. Every GC and subcontractor uses Autodesk.
- **High value:** AutoCAD subscription = $220+/yr → $20 per referral minimum
- **Placement ideas:** Project pages, bids page, sidebar on large project profiles
- [YOUR AFFILIATE LINK]:
- [YOUR TRACKING ID]:


### Bluebeam Revu
- **Program:** Direct affiliate (contact sales@bluebeam.com)
- **Sign up:** https://www.bluebeam.com/partners/
- **Commission:** Negotiated per partner (typically 10-15% on licenses)
- **Why it fits:** PDF markup / takeoff software — used by 92% of top ENR contractors
- **High value:** Bluebeam Basics = $240/yr, Core = $300/yr
- **Placement ideas:** Bids page, permits page, project detail pages
- [YOUR AFFILIATE LINK]:
- [YOUR TRACKING ID]:


### PlanGrid (Autodesk)
- **Program:** Part of Autodesk affiliate program (same sign-up as AutoCAD above)
- **Why it fits:** Field management / blueprints on mobile — superintendent-level tool
- **Placement ideas:** Project pages, gallery pages
- [YOUR AFFILIATE LINK]: (same as Autodesk)


## ── FUTURE ADDITIONS (when ready) ──────────────────────────────────────────


### Home Depot Pro
- B2B program for contractors. High AOV (average order value).
- Sign up: https://www.homedepot.com/c/SF_CS_affiliatecenter

### Lowe's for Pros
- Contractor affiliate / referral program
- Sign up: https://www.lowes.com/cd/lowes-affiliate-program/product-1000036720

### SafetyGearPro
- PPE affiliate, higher commission than Grainger (~8%)
- Sign up: https://www.safetygear.com/affiliate-program.html


## ── IMPLEMENTATION CHECKLIST ────────────────────────────────────────────────

[ ] Sign up for Milwaukee Tool affiliate
[ ] Sign up for DeWalt affiliate
[ ] Sign up for Autodesk affiliate (covers AutoCAD + PlanGrid)
[ ] Sign up for Bluebeam (email sales team)
[ ] Sign up for Grainger
[ ] Fill in affiliate links above
[ ] Run: python manage.py seed_affiliates
[ ] Verify Affiliate records appear in Django admin at /admin/construction/affiliate/
[ ] Add affiliate sidebar block to project_detail.html template
[ ] Add /affiliates/ page to construction/urls.py


## ── NOTES ON THE SEED COMMAND ───────────────────────────────────────────────
# The seed_affiliates.py management command was already created this session.
# It creates Affiliate model records from hardcoded data.
# Once you have real affiliate links, update the seed command OR
# just edit the records directly in Django admin at:
#   http://127.0.0.1:8002/admin/construction/affiliate/
#
# The Affiliate model has these fields:
#   name, slug, category (TOOLS/SOFTWARE/SAFETY/OTHER),
#   affiliate_url, commission_rate, description, logo, active, featured
#
# NOTE: Run migrations first if not already done:
#   python manage.py makemigrations construction
#   python manage.py migrate
#   python manage.py seed_affiliates
