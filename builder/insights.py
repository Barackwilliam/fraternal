"""
AI Coach — Insights engine ya dashboard.

Sehemu ya 1 (hii file): RULE-BASED insights — bure kabisa, instant, hakuna
API calls. Mfumo unachunguza hali ya website na kutoa ushauri 1-3 wenye
maana ZAIDI kwa wakati huo, kila mmoja na action link ya moja kwa moja.

Sehemu ya 2 (views.ai_suggest_items): AI bulk-suggest — kwa click moja,
AI ina-generate items 4-6 za ziada (packages/products/menu...) kwa muktadha
wa biashara, zinaingia kama HIDDEN drafts ili mtu azipitie na kuzi-publish.

Kila insight: dict(icon, title, text, action_url, action_label, priority)
priority: 1 = ya juu kabisa (inaonyeshwa kwanza)
"""
from .ai_oneshot import PRIMARY_COLLECTION


def get_insights(site):
    """Rudisha insights zilizopangwa kwa priority (max zote; view inakata top 3)."""
    insights = []

    primary_slug = PRIMARY_COLLECTION.get(site.website_type, 'services')
    primary = site.collections.filter(slug=primary_slug).first()
    items_count = primary.items.count() if primary else 0

    # ── P1: Inquiries mpya zinasubiri (pesa mezani!) ──
    new_inq = site.inquiries.filter(status='new').count()
    if new_inq > 0:
        insights.append({
            'icon': '📥',
            'title': f'{new_inq} new inquir{"y" if new_inq == 1 else "ies"} waiting',
            'text': ('Customers are waiting to hear from you — fast replies '
                     'close more deals. Reply via WhatsApp with one tap.'),
            'action_url': f'/builder/site/{site.id}/inquiries/?status=new',
            'action_label': 'Reply now',
            'priority': 1,
        })

    # ── P1: Haiko hewani ──
    if not site.is_published:
        ready = bool(site.contact_phone or site.whatsapp_number) and items_count > 0
        insights.append({
            'icon': '🚀',
            'title': 'Your website is not live yet',
            'text': ('Everything you build is invisible to customers until you '
                     'publish. ' + ('You look ready — go live!' if ready else
                     'Add your contact details and some content first, then publish.')),
            'action_url': f'/builder/site/{site.id}/#publish',
            'action_label': 'Publish',
            'priority': 1 if ready else 2,
        })

    # ── P2: Hakuna mawasiliano ──
    if not site.contact_phone and not site.whatsapp_number:
        insights.append({
            'icon': '📞',
            'title': 'Customers have no way to reach you',
            'text': ('Your phone/WhatsApp number appears on every page and '
                     'powers the booking buttons — without it, you lose every lead.'),
            'action_url': f'/builder/site/{site.id}/#settings',
            'action_label': 'Add contact details',
            'priority': 1,
        })

    # ── P2: Content chache ──
    if primary is not None and items_count < 3:
        insights.append({
            'icon': primary.icon or '🗂️',
            'title': f'Only {items_count} {primary.name.lower()} so far',
            'text': (f'Websites with 4+ {primary.name.lower()} win far more trust. '
                     f'Let AI suggest more based on your business — you review '
                     f'before anything goes live.'),
            'action_url': f'/builder/site/{site.id}/collections/{primary.id}/',
            'action_label': f'✨ AI: suggest {primary.name.lower()}',
            'priority': 2,
            'ai_suggest': True,
            'collection_id': primary.id if primary else None,
        })

    # ── P3: Hakuna tagline ──
    if not site.tagline:
        insights.append({
            'icon': '✍️',
            'title': 'No tagline yet',
            'text': ('A one-line tagline appears in your hero and browser tab — '
                     'it positions your brand instantly. The ✨ AI button can '
                     'write one for you.'),
            'action_url': f'/builder/site/{site.id}/#settings',
            'action_label': 'Write with AI',
            'priority': 3,
        })

    # ── P3: Hakuna logo ──
    if not site.logo_url:
        insights.append({
            'icon': '🖼️',
            'title': 'Add your logo',
            'text': ('A logo in the navbar makes your website look established '
                     'and trustworthy. Upload one under Website Details.'),
            'action_url': f'/builder/site/{site.id}/#settings',
            'action_label': 'Upload logo',
            'priority': 3,
        })

    # ── P3: Items bila picha ──
    if primary is not None and items_count > 0:
        no_image = primary.items.filter(image_url='').count()
        if no_image > 0:
            insights.append({
                'icon': '📷',
                'title': f'{no_image} item{"" if no_image == 1 else "s"} without photos',
                'text': ('Items with photos get dramatically more clicks and '
                         'inquiries. A phone photo with good light works great.'),
                'action_url': f'/builder/site/{site.id}/collections/{primary.id}/',
                'action_label': 'Add photos',
                'priority': 3,
            })

    # ── P4: Design haijaguswa ──
    home = site.pages.filter(slug='home').first()
    if home is not None and not home.grapes_data:
        insights.append({
            'icon': '🎨',
            'title': 'Make the design yours',
            'text': ('Your home page is using the starter design. Open the '
                     'editor to swap images, adjust colors, or drag in new '
                     'sections — everything is drag & drop.'),
            'action_url': f'/builder/site/{site.id}/pages/{home.id}/edit/',
            'action_label': 'Open editor',
            'priority': 4,
        })

    insights.sort(key=lambda i: i['priority'])
    return insights
