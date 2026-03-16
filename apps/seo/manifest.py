"""PWA Web Manifest — helps Google understand site as an app."""
import json
from django.http import JsonResponse

def web_manifest(request):
    manifest = {
        "name": "JamiiTek — Web Development & AI Bot Tanzania",
        "short_name": "JamiiTek",
        "description": "Tanzania web developer. Websites, AI WhatsApp bots, hosting & domains.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#00010a",
        "theme_color": "#00c8ff",
        "lang": "en-TZ",
        "categories": ["business", "productivity", "utilities"],
        "icons": [
            {"src": "/static/images/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/images/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "related_applications": [],
        "prefer_related_applications": False,
        "keywords": [
            "web developer Tanzania", "website development", "WhatsApp bot Tanzania",
            "AI chatbot", "JamiiBot", "web hosting Tanzania", "domain Tanzania"
        ]
    }
    return JsonResponse(manifest)