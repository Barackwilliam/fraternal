"""
Akaunti moja ya JamiiTek kwa sehemu tatu: Client Portal, JamiiBot na Web Builder.

Zote zinatumia `User` mmoja wa Django; kila sehemu ina "profile" yake:
  - Client Portal → apps.models.Client
  - JamiiBot      → apps.chatbot.models.ChatbotClient (chatbot/views._get_or_create_client)
  - Web Builder   → hahitaji profile (ClientWebsite.user)

Mtu aliyejisajili sehemu yoyote anaweza kuingia nyingine kwa username na
password zile zile — profile inayokosekana inatengenezwa hapa kwa taarifa
zilizopo (jina, email, simu, jina la biashara/website).
"""


def ensure_client_profile(user):
    """Rudisha Client ya portal kwa `user`, ukiitengeneza kama haipo."""
    from apps.models import Client

    client = Client.objects.filter(user=user).first()
    if client:
        return client

    name = user.get_full_name() or user.username
    email = user.email or ''
    phone = ''
    company = ''

    from apps.chatbot.models import ChatbotClient
    bot = ChatbotClient.objects.filter(user=user).first()
    if bot:
        name = bot.full_name or name
        email = email or bot.email or ''
        phone = bot.phone or ''
        company = bot.business_name or ''

    if not company:
        site = getattr(user, 'websites', None)
        site = site.order_by('pk').first() if site is not None else None
        if site:
            company = site.site_name

    return Client.objects.create(
        user=user, name=name[:100], email=email, phone=phone[:20], company=company[:100],
    )
