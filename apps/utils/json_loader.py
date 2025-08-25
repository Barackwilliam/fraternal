import json
import os
from pathlib import Path
from django.conf import settings

def load_website_config(website_type):
    """Load JSON config for a specific website type"""
    base_dir = Path(__file__).resolve().parent.parent.parent
    json_path = os.path.join(base_dir, 'apps', 'website_types', f'{website_type}.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Config for {website_type} not found")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in {website_type}.json")