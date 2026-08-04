# apps/site_content.py
"""
Content models for the public homepage sliders.

Images are stored as Uploadcare UUIDs (same pattern as Service / Team already
use in models.py), so the CDN handles resizing, format negotiation and quality.
Nothing is hardcoded in the template — everything below is editable from admin.

Add to apps/models.py:

    from .site_content import HeroSlide, PortfolioItem, Testimonial   # noqa

...or just paste these classes at the bottom of models.py. Then:

    python manage.py makemigrations apps
    python manage.py migrate
"""

from django.db import models

from .uploadcare_widget import cdn_base, extract_uuid


# ──────────────────────────────────────────────────────────────
# Shared Uploadcare helper
# ──────────────────────────────────────────────────────────────
class UploadcareImageMixin(models.Model):
    """Gives a model a `image` UUID field plus responsive CDN helpers."""

    image = models.CharField(
        max_length=255, blank=True,
        help_text='Uploadcare UUID only, e.g. 1a2b3c4d-5e6f-7890-abcd-ef1234567890',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Accept a bare UUID or a full ucarecdn URL — always store the UUID.
        self.image = extract_uuid(self.image)
        return super().save(*args, **kwargs)

    # -- CDN builders -------------------------------------------------
    # Same pattern as Service.get_image_url() / Team.get_image_url()
    def cdn(self, width=None, height=None, quality='smart', crop_faces=False):
        uuid = extract_uuid(self.image)
        if not uuid:
            return ''
        url = f'{cdn_base()}/{uuid}/'
        if width:
            url += f'-/resize/{width}x/'
        url += f'-/format/jpg/-/quality/{quality}/'
        return url

    def srcset(self, widths, height_ratio=None, crop_faces=False):
        """Ready-to-use srcset string. Cropping is handled by CSS object-fit."""
        if not extract_uuid(self.image):
            return ''
        return ', '.join(f'{self.cdn(w)} {w}w' for w in widths)

    # -- Template-friendly properties (no-arg, callable from Django) ---
    @property
    def url(self):
        return self.cdn(1600)

    @property
    def url_wide(self):
        return self.cdn(1920)

    @property
    def srcset_wide(self):
        return self.srcset([640, 960, 1280, 1600, 1920])

    @property
    def url_card(self):
        return self.cdn(800)

    @property
    def srcset_card(self):
        return self.srcset([400, 600, 800, 1200])

    @property
    def url_avatar(self):
        return self.cdn(160)


# ──────────────────────────────────────────────────────────────
# Hero slider
# ──────────────────────────────────────────────────────────────
class HeroSlide(UploadcareImageMixin):
    """Full-bleed photo slides at the top of the homepage."""

    eyebrow = models.CharField(
        max_length=80, blank=True,
        help_text='Small label above the headline, e.g. "Web Development"',
    )
    headline = models.CharField(
        max_length=120,
        help_text='Wrap the accented words in *asterisks*, e.g. "That *Drive Success*"',
    )
    subheadline = models.CharField(max_length=260, blank=True)

    cta_label = models.CharField(max_length=40, blank=True, default='Start Your Project')
    cta_url = models.CharField(max_length=300, blank=True, default='/get-started/')
    cta2_label = models.CharField(max_length=40, blank=True)
    cta2_url = models.CharField(max_length=300, blank=True)

    focal = models.CharField(
        max_length=20, default='center',
        choices=[('center', 'Center'), ('top', 'Top'), ('bottom', 'Bottom'),
                 ('left', 'Left'), ('right', 'Right')],
        help_text='Which part of the photo stays visible when cropped',
    )

    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def headline_html(self):
        """*word* -> <em>word</em>, escaped everywhere else."""
        from django.utils.html import escape
        from django.utils.safestring import mark_safe
        import re
        safe = escape(self.headline)
        return mark_safe(re.sub(r'\*(.+?)\*', r'<em>\1</em>', safe))

    def __str__(self):
        return self.headline[:60]

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Hero Slide'


# ──────────────────────────────────────────────────────────────
# Portfolio / work slider
# ──────────────────────────────────────────────────────────────
class PortfolioItem(UploadcareImageMixin):
    """Real client work. Use a screenshot of the live site, 1600x1200 or wider."""

    title = models.CharField(max_length=120)
    client = models.CharField(max_length=120, blank=True)
    category = models.CharField(
        max_length=60, blank=True,
        help_text='e.g. E-Commerce, School System, Tourism',
    )
    summary = models.CharField(max_length=200, blank=True)
    live_url = models.URLField(blank=True, help_text='Link to the live site')
    year = models.CharField(max_length=9, blank=True)

    is_featured = models.BooleanField(default=True, help_text='Show in the homepage slider')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} — {self.client}' if self.client else self.title

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Portfolio Item'


# ──────────────────────────────────────────────────────────────
# Testimonials
# ──────────────────────────────────────────────────────────────
class Testimonial(UploadcareImageMixin):
    """Real client quotes with real photos."""

    quote = models.TextField(max_length=400)
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=140, blank=True, help_text='e.g. CEO, Mushi Traders')
    rating = models.IntegerField(default=5, choices=[(n, f'{n} stars') for n in range(1, 6)])

    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    @property
    def initials(self):
        bits = [p for p in self.name.split() if p]
        return ''.join(p[0] for p in bits[:2]).upper() or '?'

    def __str__(self):
        return f'{self.name} ({self.rating}★)'

    class Meta:
        ordering = ['order', 'id']