from django.core.management.base import BaseCommand
import json
import os
from pathlib import Path

DEFAULT_TYPES = [
    "ecommerce", "company_profile", "real_estate", 
    "school", "booking", "travel", "ngo", "news",
    "hospital", "portfolio", "membership", "restaurant",
    "jobboard", "photography", "events", "courses",
    "betting", "crypto", "dashboard", "auction",
    "forum", "saas"
]

class Command(BaseCommand):
    help = 'Initialize default website type JSON files'

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        target_dir = os.path.join(base_dir, 'apps', 'website_types')
        
        os.makedirs(target_dir, exist_ok=True)
        
        for website_type in DEFAULT_TYPES:
            file_path = os.path.join(target_dir, f'{website_type}.json')
            if not os.path.exists(file_path):
                default_config = {
                    "sample_question": {
                        "question": f"Sample question for {website_type}",
                        "type": "text"
                    }
                }
                with open(file_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                self.stdout.write(f'Created {file_path}')



# command to run this script
# python manage.py init_website_types