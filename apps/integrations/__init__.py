"""
Registry ya providers.

Kuongeza provider mpya = class moja + mstari mmoja hapa.
Hakuna migration, hakuna mabadiliko kwenye views wala templates.
"""
from .base import AdapterError, BaseAdapter  # noqa: F401
from .cloudflare import CloudflareAdapter
from .rdap import DomainAdapter
from .render import RenderAdapter
from .supabase import SupabaseAdapter
from .uploadcare import UploadcareAdapter

ADAPTERS = {
    RenderAdapter.provider: RenderAdapter,
    CloudflareAdapter.provider: CloudflareAdapter,
    DomainAdapter.provider: DomainAdapter,
    SupabaseAdapter.provider: SupabaseAdapter,
    UploadcareAdapter.provider: UploadcareAdapter,
}


def get_adapter_class(provider):
    cls = ADAPTERS.get(provider)
    if cls is None:
        raise AdapterError(f'Provider haijulikani: {provider}')
    return cls


def get_adapter(integration):
    return get_adapter_class(integration.provider)(integration)


def provider_choices():
    return [(k, c.label) for k, c in ADAPTERS.items()]
