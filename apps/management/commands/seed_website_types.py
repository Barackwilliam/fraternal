from django.core.management.base import BaseCommand
from apps.models import WebsiteType

WEBSITE_TYPES = [
    ("E- commerce", "Online store platform | Duka la mtandaoni"),
    ("Company Profile", "Business showcase website | Wasifu wa kampuni"),
    ("Real Estate", "Property listing platform | Jukwaa la kuuza mali"),
    ("School/College", "Educational institution site | Tovuti ya shule/chuo"),
    ("Online Booking", "Appointment reservation system | Mfumo wa kuhifadhi nafasi"),
    ("Travel & Tourism", "Travel agency platform | Jukwaa la usafiri na utalii"),
    ("NGO/Charity", "Non-profit organization site | Tovuti ya shirika la misada"),
    ("News/Blog", "Content publishing platform | Jukwaa la habari na blogu"),
    ("Hospital/Clinic", "Healthcare management site | Tovuti ya afya na matibabu"),
    ("Personal Portfolio", "Professional work showcase | Onyesho la kazi za kitaalamu"),
    ("Membership", "Subscription-based platform | Jukwaa la usajili"),
    ("Restaurant", "Food ordering and menu site | Tovuti ya maagizo ya chakula"),
    ("Job Board", "Employment listing platform | Jukwaa la kazi na ajira"),
    ("Photography", "Photo gallery website | Tovuti ya maonyesho ya picha"),
    ("Events", "Event management system | Mfumo wa mikutano na hafla"),
    ("Online Courses", "E-learning platform | Jukwaa la masomo ya mtandaoni"),
    ("Betting", "Sports betting platform | Jukwaa kamari za michezo"),
    ("Cryptocurrency", "Blockchain financial platform | Jukwaa la fedha za kidijitali"),
    ("Dashboard", "Data visualization system | Mfumo wa uonyeshaji wa data"),
    ("Auction", "Online bidding platform | Jukwaa la mnada wa mtandaoni"),
    ("Forum", "Community discussion board | Jukwaa la majadiliano"),
    ("SaaS", "Software service platform | Jukwaa la programu kama huduma")
]

class Command(BaseCommand):
    help = 'Seed website types data'

    def handle(self, *args, **options):
        for name, desc in WEBSITE_TYPES:
            WebsiteType.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded website types'))