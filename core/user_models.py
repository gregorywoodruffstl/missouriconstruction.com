"""
User Profile Model - Citizen and Business Owner Accounts
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile for both Citizens and Business Owners
    Citizens register FREE to set default Springfield, write reviews, bookmark
    Business Owners claim listings and manage Premium/Featured subscriptions
    """
    USER_TYPE_CHOICES = [
        ('CITIZEN', 'Citizen/Resident'),
        ('BUSINESS', 'Business Owner'),
        ('ADMIN', 'Site Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='CITIZEN')
    
    # Default City Preference (USER REQUESTED - cookie/IP-based with override)
    default_city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_users')
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    # Email Preferences
    email_weekly_digest = models.BooleanField(default=True)  # "This Week in Springfield, MO"
    email_new_businesses = models.BooleanField(default=True)
    email_new_events = models.BooleanField(default=True)
    
    # Engagement Tracking (for leaderboards, badges)
    review_count = models.IntegerField(default=0)
    event_submissions = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    bookmark_count = models.IntegerField(default=0)
    
    # Business Association (if user_type == BUSINESS)
    # Links to Business model via Business.managers ManyToMany
    
    # Verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe (for business owners)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    @property
    def is_business_owner(self):
        return self.user_type == 'BUSINESS'
    
    @property
    def managed_businesses(self):
        """Get all businesses this user manages"""
        from .models import Business
        return Business.objects.filter(managers=self.user)


# Auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class BusinessReview(models.Model):
    """
    Citizen reviews of businesses (like Google/Yelp)
    Admin approval required initially (USER REQUESTED)
    """
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')
    
    # Review Content
    rating = models.IntegerField(choices=[(1,'⭐'), (2,'⭐⭐'), (3,'⭐⭐⭐'), (4,'⭐⭐⭐⭐'), (5,'⭐⭐⭐⭐⭐')])
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Photos (optional)
    photos = models.JSONField(default=list, blank=True)  # Array of image URLs
    
    # Moderation (USER REQUESTED: Admin approval initially)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews_approved')
    
    flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=500, blank=True)
    
    # Business Response (business owner can reply to review)
    business_response = models.TextField(blank=True)
    business_response_date = models.DateTimeField(null=True, blank=True)
    
    # Helpfulness (other users vote)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['business', 'user']  # One review per user per business
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', '-created_at']),
            models.Index(fields=['approved', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} reviewed {self.business.name} - {self.rating}⭐"
    
    @property
    def helpfulness_score(self):
        """Calculate helpfulness percentage"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return int((self.helpful_count / total) * 100)


class BusinessClaim(models.Model):
    """
    Track business ownership verification process
    USER REQUESTED: Email link verification
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified - Approved'),
        ('REJECTED', 'Rejected - Denied'),
    ]
    
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='claims')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_claims')
    
    # Verification Method (USER REQUESTED: Email link)
    verification_method = models.CharField(max_length=20, default='EMAIL')
    verification_token = models.CharField(max_length=100)  # Unique token for email link
    verification_code = models.CharField(max_length=10, blank=True)  # Optional 6-digit code
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Admin Review (if needed)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claims_reviewed')
    review_notes = models.TextField(blank=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} claims {self.business.name} ({self.status})"


class Bookmark(models.Model):
    """
    Citizen bookmarks for businesses, articles, events
    """
    BOOKMARK_TYPE_CHOICES = [
        ('BUSINESS', 'Business'),
        ('ARTICLE', 'Article'),
        ('EVENT', 'Event'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    bookmark_type = models.CharField(max_length=10, choices=BOOKMARK_TYPE_CHOICES)
    
    # Polymorphic relations (only one will be set)
    business = models.ForeignKey('Business', on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    article = models.ForeignKey('Article', on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['user', 'business'],
            ['user', 'article'],
            ['user', 'event'],
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.business:
            return f"{self.user.username} bookmarked {self.business.name}"
        elif self.article:
            return f"{self.user.username} bookmarked {self.article.title}"
        elif self.event:
            return f"{self.user.username} bookmarked {self.event.title}"
