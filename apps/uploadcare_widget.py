# apps/uploadcare_widget.py
"""
A real "upload a file" button for Uploadcare UUID fields in Django admin.

Uses the same Uploadcare 3.x widget the project already loads in
ServiceAdminForm / TeamAdminForm, so nothing new is introduced.

Usage:

    from .uploadcare_widget import UploadcareImageWidget, extract_uuid

    class MyForm(forms.ModelForm):
        class Meta:
            model = MyModel
            fields = '__all__'
            widgets = {'image': UploadcareImageWidget(crop='16:9')}
"""

import re

from django import forms
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

UUID_RE = re.compile(
    r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?:~\d+)?)',
    re.IGNORECASE,
)


def extract_uuid(value):
    """
    Accepts anything Uploadcare might hand back and returns the bare UUID:

        '1a2b...ef12'                            -> '1a2b...ef12'
        'https://ucarecdn.com/1a2b...ef12/'      -> '1a2b...ef12'
        'https://ucarecdn.com/1a2b.../-/crop/'   -> '1a2b...ef12'

    Returns '' if nothing UUID-shaped is present.
    """
    if not value:
        return ''
    match = UUID_RE.search(str(value))
    return match.group(1).lower() if match else ''


def public_key():
    return (getattr(settings, 'UPLOADCARE', {}) or {}).get('pub_key', '')


def cdn_base():
    """Same host the project already uses in Service.get_image_url()."""
    return 'https://ucarecdn.com'


class UploadcareImageWidget(forms.TextInput):
    """Renders an Uploadcare upload button plus a live thumbnail."""

    class Media:
        js = ['https://ucarecdn.com/libs/widget/3.x/uploadcare.full.min.js']

    def __init__(self, attrs=None, crop=None, images_only=True):
        defaults = {
            'role': 'uploadcare-uploader',
            'data-public-key': public_key(),
            'data-preview-step': 'true',
            'data-clearable': 'true',
            'data-tabs': 'file camera url facebook gdrive dropbox instagram',
        }
        if images_only:
            defaults['data-images-only'] = 'true'
        if crop:
            # e.g. '16:9', '1:1', '4:3' — forces the right shape at upload time
            defaults['data-crop'] = crop
        defaults.update(attrs or {})
        super().__init__(attrs=defaults)

    def render(self, name, value, attrs=None, renderer=None):
        uuid = extract_uuid(value)
        html = super().render(name, uuid, attrs, renderer)

        if uuid:
            preview = format_html(
                '<div style="margin-top:10px">'
                '<img src="{}/{}/-/resize/320x/-/format/jpg/-/quality/smart/" '
                'style="max-height:150px;border-radius:8px;border:1px solid #ddd;'
                'display:block">'
                '<code style="font-size:11px;color:#666">{}</code></div>',
                cdn_base(), uuid, uuid,
            )
        else:
            preview = mark_safe(
                '<p style="margin-top:8px;color:#888;font-size:12px">'
                'No image yet — click the upload button above.</p>'
            )

        if not public_key():
            preview = mark_safe(
                '<p style="margin-top:8px;color:#b32d2e;font-size:12px">'
                '<strong>UPLOADCARE_PUB_KEY is not set</strong> — the upload button '
                'will not appear. Set it in your environment and restart.</p>'
            ) + preview

        return mark_safe(html + preview)

    def value_from_datadict(self, data, files, name):
        """Store the bare UUID no matter what the widget submitted."""
        return extract_uuid(super().value_from_datadict(data, files, name))