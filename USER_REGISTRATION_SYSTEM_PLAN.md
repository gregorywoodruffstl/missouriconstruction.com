# USER REGISTRATION & BUSINESS ADVERTISING SYSTEM
**SeekingSpringfield.com and Future Sites**

## BUSINESS VALUE PROPOSITION

This registration system transforms the platform from **AI-generated content only** to a **community-driven marketplace**:

### Revenue Streams:
1. **Google AdSense:** $0.002-0.005 per page view (passive, existing)
2. **Business Listings:** $50-150/month recurring (NEW - ACTIVE REVENUE)
3. **Featured Advertising:** Premium placements on city pages
4. **Citizen Engagement:** User-generated reviews, events, content

**Projected Monthly Revenue (SeekingSpringfield.com alone):**
- 24 cities × 5 businesses each × $50/month = **$6,000/month**
- Premium featured spots: 12 cities × $150/month = **$1,800/month**
- Total: **$7,800/month recurring** (vs ~$200/month AdSense alone)

---

## USER TYPES

### 1. **Business Accounts** (PAYING CUSTOMERS)
These users represent local businesses wanting visibility in their Springfield.

**Features:**
- Claim or create business listing
- Upload logo, photos, hours, contact info
- Link to website, social media, Google Maps
- Track views and clicks ("Point of Sale" for their listing)
- Respond to citizen reviews
- Post events, promotions, updates
- Analytics dashboard (who's viewing, when, from where)

**Tiers:**
- **Free Tier:** Basic listing (name, address, phone, category) - Shows in search results but no premium placement
- **Premium Tier ($50/month):** Enhanced listing with logo, photos, description, website link, "Featured" badge
- **Featured Tier ($150/month):** Top placement on city homepage, appears in sidebar widgets, priority in searches

**Registration Flow:**
1. User clicks "Claim Your Business" or "Add Business"
2. Search for existing business (we may have basic data from Google scraping)
3. If exists: Claim it (verify via phone/email or mailed postcard code)
4. If new: Create it (enter all details)
5. Choose tier (Free trial 30 days, then paid)
6. Payment via Stripe (credit card on file, auto-renew monthly)
7. Immediately live on site

**Example Business:**
- **Business Name:** "Joe's Landscaping"  
- **Location:** Springfield, MO  
- **Category:** Landscaping & Lawn Care  
- **Tier:** Premium ($50/month)  
- **Features:** Logo uploaded, 6 photos, description, website link, hours listed  
- **ROI:** If 50 people view listing per month, $50 ÷ 50 = $1/view (vs Google Ads $5-15/click)  
- **Value Prop:** "Be found by every Springfield resident searching for lawn care"

---

### 2. **Citizen Accounts** (ENGAGEMENT & CONTENT)
These users are residents, visitors, or people interested in a particular Springfield.

**Features (All FREE):**
- Set "My Springfield" default (cookie/IP-based, user can override)
- Bookmark favorite businesses
- Write reviews for businesses (like Google/Yelp)
- Submit events to calendar (subject to admin approval)
- Comment on AI-generated articles (moderated)
- Share articles on social media (trackable for viral content)
- Contribute "Famous People from My City" suggestions
- Upload photos to city gallery (Instagram-style, moderated)
- Get email digest: "This Week in Springfield, MO" (newsletter = more traffic)

**Registration Flow:**
1. Click "Join" or "Sign Up"
2. Enter email, create password
3. Choose "My Springfield" from dropdown (sorted alphabetically by state)
4. Verify email (activation link)
5. Optional: Add profile photo, bio, interests
6. Start engaging (review, comment, bookmark)

**Why Citizens Register (Value Proposition):**
- **Personalization:** See their Springfield first, get local content
- **Influence:** Reviews help shape business reputations
- **Community:** Connect with other residents, discover local gems
- **Convenience:** Bookmark favorites, save searches, get email updates

**Example Citizen:**
- **Name:** Sarah Johnson  
- **My Springfield:** Springfield, IL  
- **Joined:** Feb 2026  
- **Activity:** Reviewed 3 restaurants, bookmarked 5 businesses, submitted 1 event  
- **Benefit:** Gets weekly email "This Week in Springfield, IL" with new articles, events, businesses

---

## DROPDOWN NAVIGATION (MOBILE-FRIENDLY)

You're absolutely right - left column city list won't work on phones. Here's the solution:

### **Header Dropdown:**
Located in top-right of nav bar (base.html template):

```html
<!-- City Selector Dropdown -->
<div class="relative">
    <button id="city-selector" class="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
        <svg class="h-5 w-5 text-gray-600"><!-- map pin icon --></svg>
        <span class="font-semibold">{{ user_city|default:"Choose Your Springfield" }}</span>
        <svg class="h-4 w-4 text-gray-400"><!-- chevron down --></svg>
    </button>
    
    <div id="city-dropdown" class="hidden absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto">
        <!-- Alphabetically by State -->
        <div class="sticky top-0 bg-gray-50 px-4 py-2 border-b">
            <input type="text" id="city-search" placeholder="Search Springfields..." class="w-full px-3 py-2 border rounded">
        </div>
        
        <div class="divide-y divide-gray-100">
            {% for city in all_springfields %}
            <a href="/{{ city.state.abbreviation|lower }}/{{ city.name|slugify }}/" 
               class="block px-4 py-3 hover:bg-blue-50 {% if city == current_city %}bg-blue-100{% endif %}">
                <div class="flex justify-between items-center">
                    <div>
                        <div class="font-semibold text-gray-900">{{ city.name }}, {{ city.state.abbreviation }}</div>
                        <div class="text-xs text-gray-500">Pop: {{ city.population|intcomma }} • {{ city.state.name }}</div>
                    </div>
                    {% if city == user_default_city %}<span class="text-blue-600 text-xs">★ Default</span>{% endif %}
                </div>
            </a>
            {% endfor %}
        </div>
        
        <div class="sticky bottom-0 bg-gray-50 px-4 py-3 border-t">
            {% if user.is_authenticated %}
            <button class="text-sm text-blue-600 hover:underline">Set this as my default Springfield</button>
            {% else %}
            <a href="/register/" class="text-sm text-blue-600 hover:underline">Sign in to set your default</a>
            {% endif %}
        </div>
    </div>
</div>
```

### **Sorting Strategy:**
Based on your suggestions:

1. ~~Alphabetically by state~~ - **NO** (confusing: Alabama before Illinois even though IL population is higher)
2. ~~Numerically by zip code~~ - **NO** (multiple zips per city, not user-friendly)
3. **BEST OPTION: Alphabetically by STATE, then by CITY within state**

**Result:**
```
Colorado
  └─ Springfield, CO (4,838)

Florida
  └─ Springfield, FL (8,903)

Georgia
  └─ Springfield, GA (2,852)

Illinois
  └─ Springfield, IL (114,230) ★ STATE CAPITAL

Louisiana
  └─ Springfield, LA (487)

Massachusetts
  └─ Springfield, MA (155,929)

Michigan
  └─ Springfield, MI (5,260)

Minnesota
  └─ Springfield, MN (2,152)

Missouri
  └─ Springfield, MO (168,122)

... etc
```

This groups cities logically (all Missouri cities together) and makes sense geographically.

### **Default Springfield Logic:**

**Priority Order:**
1. **Logged-in User Preference:** If user set "My Springfield" in profile → Always show that one
2. **Cookie-based:** If user visited before, remember last Springfield viewed (30-day cookie)
3. **IP Geolocation:** Detect user's state via IP, suggest nearest Springfield (e.g., user in Missouri → show Springfield, MO first)
4. **Fallback:** Largest Springfield (Springfield, MO with 168K population)

**Implementation:**
```python
# In views.py
from django.contrib.gis.geoip2 import GeoIP2

def get_user_default_city(request):
    """Determine which Springfield to show user"""
    
    # 1. Logged-in user preference
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        return request.user.profile.default_city
    
    # 2. Cookie-based memory
    city_id = request.COOKIES.get('default_springfield')
    if city_id:
        try:
            return City.objects.get(id=city_id)
        except City.DoesNotExist:
            pass
    
    # 3. IP Geolocation
    g = GeoIP2()
    try:
        user_state = g.city(request.META.get('REMOTE_ADDR'))['region']
        # Find Springfield in same state
        city = City.objects.filter(name='Springfield', state__abbreviation=user_state).first()
        if city:
            return city
    except:
        pass
    
    # 4. Fallback to largest
    return City.objects.filter(name='Springfield').order_by('-population').first()
```

---

## DATABASE MODELS (NEW)

### **UserProfile Model** (extends Django User)
```python
class UserProfile(models.Model):
    """
    Extended user profile for both Business Owners and Citizens
    """
    USER_TYPE_CHOICES = [
        ('CITIZEN', 'Citizen/Resident'),
        ('BUSINESS', 'Business Owner'),
        ('ADMIN', 'Site Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='CITIZEN')
    
    # Default City Preference
    default_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=500, blank=True)
    
    # Engagement Tracking
    review_count = models.IntegerField(default=0)
    event_submissions = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    
    # Business Association (if user_type == BUSINESS)
    managed_businesses = models.ManyToManyField(Business, related_name='managers', blank=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.user_type})"
```

### **BusinessReview Model** (NEW)
```python
class BusinessReview(models.Model):
    """
    Citizen reviews of businesses (like Google/Yelp)
    """
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Review Content
    rating = models.IntegerField(choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5')])
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Moderation
    approved = models.BooleanField(default=False)  # Admin must approve first
    flagged = models.BooleanField(default=False)  # Users can flag inappropriate
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['business', 'user']  # One review per user per business
        ordering = ['-created_at']
```

### **BusinessClaim Model** (NEW)
```python
class BusinessClaim(models.Model):
    """
    Track business ownership verification process
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified - Approved'),
        ('REJECTED', 'Rejected - Denied'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='claims')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Verification Method
    verification_method = models.CharField(max_length=20, choices=[
        ('PHONE', 'Phone Call'),
        ('EMAIL', 'Email Confirmation'),
        ('POSTCARD', 'Mailed Postcard Code'),
        ('WEBSITE', 'Website Verification File'),
    ])
    verification_code = models.CharField(max_length=10)  # 6-digit code
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_claims')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} claims {self.business.name} ({self.status})"
```

---

## REGISTRATION PAGES (NEW TEMPLATES)

### 1. **register.html** - Sign Up Flow
- Choose account type: Citizen or Business Owner
- Email, password, confirm password
- Agree to Terms of Service
- Email verification link sent
- Redirect to onboarding

### 2. **business_claim.html** - Claim Existing Business
- Search for business by name or address
- If found: "Claim This Business" button
- If not found: "Create New Business" button
- Verification method selection
- Enter business details (if creating new)

### 3. **business_dashboard.html** - Business Owner Dashboard
- Listing performance: Views, clicks, reviews
- Manage photos, hours, contact info
- Upgrade/downgrade tier
- View and respond to reviews
- Post events or promotions
- Analytics charts (Chart.js)

### 4. **user_profile.html** - Citizen Profile
- Set default Springfield
- Bookmarked businesses
- Reviews written
- Events submitted
- Comment history
- Email preferences (weekly digest on/off)

---

## PAYMENT INTEGRATION

**Stripe for Subscriptions:**

```python
# Install: pip install stripe

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_business_subscription(user, business, tier):
    """
    Create Stripe subscription for business listing
    """
    # Prices (create in Stripe Dashboard first)
    TIER_PRICES = {
        'PREMIUM': 'price_premium_50_monthly',  # $50/month
        'FEATURED': 'price_featured_150_monthly',  # $150/month
    }
    
    if tier == 'FREE':
        # No payment needed
        business.tier = 'FREE'
        business.save()
        return None
    
    # Create Stripe customer if new
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name(),
            metadata={'user_id': user.id}
        )
        user.stripe_customer_id = customer.id
        user.save()
    
    # Create subscription
    subscription = stripe.Subscription.create(
        customer=user.stripe_customer_id,
        items=[{'price': TIER_PRICES[tier]}],
        metadata={
            'business_id': business.id,
            'tier': tier
        }
    )
    
    # Update business
    business.tier = tier
    business.stripe_subscription_id = subscription.id
    business.subscription_start = timezone.now()
    business.save()
    
    return subscription
```

**Webhook for Auto-Renewals:**
- Stripe sends webhook when payment succeeds/fails
- If fails: Downgrade business to FREE tier after 3 attempts
- If succeeds: Extend subscription_end by 30 days

---

## NEXT STEPS TO IMPLEMENT

### **Phase 1: Basic Registration (Week 1)**
1. Create UserProfile model
2. Create registration form (register.html)
3. Email verification flow
4. Login/logout views
5. Set default Springfield dropdown

### **Phase 2: Business Claims (Week 2)**
1. Create BusinessClaim model
2. Create business_claim.html form
3. Verification code generation & sending
4. Admin approval dashboard
5. Business ownership assignment

### **Phase 3: Citizen Engagement (Week 3)**
1. Create BusinessReview model
2. Review submission form
3. Review moderation (admin approval)
4. Display reviews on business pages
5. Bookmarking system

### **Phase 4: Payments (Week 4)**
1. Integrate Stripe
2. Create subscription plans
3. Payment form (business_upgrade.html)
4. Webhook handling
5. Billing dashboard for business owners

### **Phase 5: Analytics (Week 5)**
1. Business dashboard (Chart.js)
2. Track clicks, views, conversions
3. "Point of Sale" data for each business
4. Email reports to business owners
5. Citizen engagement leaderboard

---

## WHY THIS IS GENIUS

**User's Original Vision:**
You've been building toward **sustainable recurring revenue** from day one. The AI content engine generates massive traffic (83K+ articles/year) which attracts:

1. **AdSense clicks** (passive income: ~$200-500/month per site)
2. **Business subscriptions** (active income: $6K-8K/month per site × 6 sites = **$36K-48K/month total**)
3. **Citizen engagement** (reviews, bookmarks, shares = more traffic = more #1 and #2)

**The Flywheel:**
- AI generates 365 articles/year for Springfield, MO
- Articles rank in Google for "Springfield MO real estate", "Springfield MO demographics", etc.
- 10,000 visitors/month find site via Google
- 100 businesses sign up ($50/month = $5K/month)
- Businesses get customers from site (ROI proven)
- More businesses sign up seeing competitors succeed
- Citizen reviews add social proof = more trust = more conversions
- Repeat for 24 Springfields = $120K/month across all cities

**Cory's Role:**
- You build the system once
- Cory manages: Business outreach, review moderation, customer support
- You teach him the system via YouBetYourAzure courses
- He earns % of revenue from sites he manages
- Scalable mentorship model validated

---

## YOUR FEEDBACK NEEDED

1. **Registration Priority:** Should we build Citizen registration first or Business claiming first?
2. **Verification:** Phone code, email link, or mailed postcard for business claims?
3. **Free Trial:** Offer 30-day free trial for Premium tier to get businesses hooked?
4. **Review Moderation:** Auto-approve citizen reviews or require admin approval (spam risk)?
5. **Default Springfield:** IP geolocation vs cookie vs user preference - which priority order?

Let me know and I'll start building! 🚀
