# apps/management/commands/process_scheduled_actions.py
"""
Amri hii inatekeleza vitendo vilivyopangwa (scheduled actions).
Run kwa cron kila dakika: * * * * * python manage.py process_scheduled_actions

Au kwa dakika 5: */5 * * * * python manage.py process_scheduled_actions
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apps.models import ScheduledAction, ManagedWebsite, WebsiteFeature, ClientNotification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Tekeleza vitendo vilivyopangwa ambavyo wakati wake umefika'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Pata vitendo vyote vilivyopangwa ambavyo wakati wake umefika
        pending_actions = ScheduledAction.objects.filter(
            status='pending',
            scheduled_at__lte=now
        ).select_related('website', 'website__client')

        if not pending_actions.exists():
            # Also check for auto-expiry
            self._check_auto_expiry()
            self.stdout.write('Hakuna vitendo vya kutekeleza.')
            return

        count = 0
        for action in pending_actions:
            try:
                self._execute_action(action)
                count += 1
            except Exception as e:
                action.status = 'failed'
                action.result_message = str(e)
                action.executed_at = now
                action.save()
                logger.error(f"Action {action.pk} imeshindwa: {e}")

        # Also check for auto-expiry
        self._check_auto_expiry()
        self._send_expiry_warnings()

        self.stdout.write(
            self.style.SUCCESS(f'✅ Vitendo {count} vimetekelezwa kikamilifu.')
        )

    def _execute_action(self, action):
        website = action.website
        data = action.action_data or {}
        now = timezone.now()

        self.stdout.write(f'  ⚡ Inatekeleza: {action.action_type} → {website.name}')

        if action.action_type == 'suspend':
            website.status = 'suspended'
            website.suspension_reason = data.get('reason', 'Imesimamishwa kiotomatiki')
            msg = data.get('message', '')
            if msg:
                website.suspension_message = msg
            website.save()
            
            if data.get('notify_client') and website.client.email:
                self._send_email(
                    website,
                    'suspended',
                    f'Huduma ya Website Yako Imesimamishwa - {website.name}',
                    f"""Habari {website.client.name},

Website yako ({website.name}) imesimamishwa kiotomatiki.

Sababu: {data.get('reason', 'Malipo ya hosting hayajalipwa')}

Wasiliana nasi kwa msaada zaidi.

JamiiTek Team"""
                )

        elif action.action_type == 'restore':
            website.status = 'active'
            website.suspension_reason = ''
            website.save()

            if data.get('notify_client') and website.client.email:
                self._send_email(
                    website,
                    'restored',
                    f'Website Yako Imerudishwa - {website.name}',
                    f"""Habari {website.client.name},

Tunafurahi kukuarifu kwamba website yako ({website.name}) sasa inafanya kazi tena.

URL: {website.url}

Asante,
JamiiTek Team"""
                )

        elif action.action_type == 'maintenance':
            website.status = 'maintenance'
            msg = data.get('message', 'Website iko katika matengenezo.')
            website.suspension_message = msg
            website.save()

        elif action.action_type == 'send_email':
            if website.client.email:
                self._send_email(
                    website,
                    'custom',
                    data.get('email_subject', 'Taarifa kutoka JamiiTek'),
                    data.get('email_body', '')
                )

        elif action.action_type == 'disable_feature':
            feature_key = data.get('feature_key')
            if feature_key:
                try:
                    feature = WebsiteFeature.objects.get(website=website, feature_key=feature_key)
                    feature.is_enabled = False
                    feature.disabled_reason = data.get('reason', 'Imezimwa kiotomatiki')
                    feature.save()
                except WebsiteFeature.DoesNotExist:
                    pass

        elif action.action_type == 'enable_feature':
            feature_key = data.get('feature_key')
            if feature_key:
                try:
                    feature = WebsiteFeature.objects.get(website=website, feature_key=feature_key)
                    feature.is_enabled = True
                    feature.disabled_reason = ''
                    feature.save()
                except WebsiteFeature.DoesNotExist:
                    pass

        # Mark as completed
        action.status = 'completed'
        action.executed_at = now
        action.result_message = f'Imetekelezwa kikamilifu saa {now.strftime("%d/%m/%Y %H:%M")}'
        action.save()

    def _check_auto_expiry(self):
        """Simamisha websites zilizokwisha bila malipo"""
        from datetime import date
        today = date.today()
        
        expired_websites = ManagedWebsite.objects.filter(
            status='active',
            auto_suspend_on_expiry=True,
            hosting_end_date__lt=today
        )

        for website in expired_websites:
            website.status = 'suspended'
            website.suspension_reason = 'Hosting ilimalizika bila kulipa'
            website.save()
            
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  Auto-suspended: {website.name} (expired {website.hosting_end_date})')
            )

            if website.client.email and website.send_expiry_warnings:
                self._send_email(
                    website,
                    'suspension_warning',
                    f'Huduma ya Website Imesimamishwa - Malipo Inahitajika',
                    f"""Habari {website.client.name},

Hosting ya website yako ({website.name}) imemalizika tarehe {website.hosting_end_date.strftime('%d/%m/%Y')} na huduma imesimamishwa.

Ili kuendelea kutumia huduma yetu, tafadhali lipa ankara yako haraka.

Wasiliana nasi kwa maelezo zaidi.

JamiiTek Team"""
                )

    def _send_expiry_warnings(self):
        """Tuma onyo kwa websites zinazokaribia kuisha"""
        from datetime import date
        today = date.today()

        websites = ManagedWebsite.objects.filter(
            status='active',
            send_expiry_warnings=True,
        )

        for website in websites:
            days_left = (website.hosting_end_date - today).days
            
            if days_left == website.warning_days_before or days_left == 3 or days_left == 1:
                # Avoid duplicate warnings on same day
                already_sent = ClientNotification.objects.filter(
                    website=website,
                    notification_type='payment_reminder',
                    sent_at__date=today
                ).exists()

                if not already_sent and website.client.email:
                    self._send_email(
                        website,
                        'payment_reminder',
                        f'Kumbusho: Hosting Inaisha Siku {days_left} - {website.name}',
                        f"""Habari {website.client.name},

Hosting ya website yako ({website.name}) itaisha tarehe {website.hosting_end_date.strftime('%d/%m/%Y')} ({days_left} siku zilizobaki).

Tafadhali lipa ankara yako mapema ili kuepuka kusimamishwa kwa huduma.

Wasiliana nasi:
- Email: {getattr(settings, 'SUPPORT_EMAIL', 'info@jamiitek.com')}
- Simu: {getattr(settings, 'SUPPORT_PHONE', '+255 000 000 000')}

Asante,
JamiiTek Team"""
                    )
                    self.stdout.write(f'  📧 Onyo limetumwa: {website.name} ({days_left} siku)')

    def _send_email(self, website, notification_type, subject, message):
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
                recipient_list=[website.client.email],
                fail_silently=True,
            )
            ClientNotification.objects.create(
                website=website,
                client=website.client,
                notification_type=notification_type,
                subject=subject,
                message=message,
                email_sent=True
            )
        except Exception as e:
            logger.error(f"Email kushindwa kutumwa kwa {website.client.email}: {e}")
