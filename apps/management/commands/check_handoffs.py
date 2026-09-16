"""
Kufuatilia wateja wanaosubiri binadamu.

PENGO LILILOKUWEPO

`handoff.remind_owner_if_stale` inaita tu mteja **anapoandika tena**.
Lakini mteja ameambiwa "subiri" — kwa hiyo anasubiri kimya. Hali ya
kawaida kabisa, mteja anayetii maagizo, ndiyo isiyokuwa na kumbusho
lolote.

Nilikuwa nimeandika kumbusho linalotegemea kitu kisichotokea.

Hii inakimbia kwa saa, si kwa ujumbe.

RATIBA

    dakika 15  — kumbusho la kwanza kwa mmiliki
    saa 1      — kumbusho la pili KWA MMILIKI
                 + ujumbe wa ukweli KWA MTEJA
    saa 4      — la mwisho, likiwa na onyo

UJUMBE KWA MTEJA — KWA NINI TUNAVUNJA SHERIA YA UKIMYA

Tuliamua bot inyamaze kabisa baada ya handoff, ili ahadi ya "mtu halisi
anakuja" isiwe uongo. Hiyo ni sahihi kwa dakika chache.

Lakini kunyamaza kwa saa nne si uaminifu — ni kumtelekeza. Mteja
hajui kama ameonekana, kama mfumo umevunjika, au kama amesahauliwa.

Kwa hiyo baada ya saa moja, ujumbe MMOJA unaosema ukweli na kumpa
njia nyingine. Mmoja tu, kisha kimya tena.
"""
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger('chatbot.handoff')

# Dakika ambazo mmiliki anakumbushwa
OWNER_PINGS = [15, 60, 240]

# Baada ya dakika ngapi mteja anaambiwa ukweli
CUSTOMER_AFTER = 60


class Command(BaseCommand):
    help = "Kumbusha mmiliki kuhusu wateja wanaosubiri binadamu"

    def add_arguments(self, parser):
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument('--dry', action='store_true')

    def handle(self, *args, **opts):
        from apps.chatbot.models import Conversation
        from apps.chatbot import bridge

        quiet, dry = opts['quiet'], opts['dry']
        now = timezone.now()

        waiting = (Conversation.objects
                   .filter(is_human_handoff=True, handoff_at__isnull=False)
                   .select_related('bot', 'bot__client')
                   .order_by('handoff_at'))

        if not waiting.exists():
            if not quiet:
                self.stdout.write('Hakuna anayesubiri.')
            return

        owner_pings = customer_msgs = 0

        for conv in waiting:
            bot = conv.bot
            if not bot.is_active or bot.status != 'active':
                continue

            mins = int((now - conv.handoff_at).total_seconds() // 60)
            done = list(conv.metadata.get('handoff_pings') or [])
            changed = False

            # ── Mmiliki ──
            due = [m for m in OWNER_PINGS if mins >= m and m not in done]
            if due and bot.notify_handoff and bot.owner_digits:
                level = max(due)
                if dry:
                    self.stdout.write(self.style.HTTP_INFO(
                        f"\n── kwa mmiliki ({bot.bot_name}, dakika {mins}) ──"))
                    self.stdout.write(self._owner_text(conv, mins, level))
                else:
                    wa = bridge.BaileysHandler(bot)
                    res = wa.send_text(bot.owner_whatsapp, self._owner_text(conv, mins, level))
                    if not res.get('success'):
                        logger.error('[%s] kumbusho la handoff halikufika: %s',
                                     bot.session_name, res.get('error'))
                        continue
                done.extend(due)
                changed = True
                owner_pings += 1

            # ── Mteja ──
            if (mins >= CUSTOMER_AFTER
                    and not conv.metadata.get('handoff_customer_told')):
                text = self._customer_text(bot)
                if dry:
                    self.stdout.write(self.style.HTTP_INFO(
                        f"\n── kwa mteja ({conv.customer_phone}) ──"))
                    self.stdout.write(text)
                else:
                    wa = bridge.BaileysHandler(bot, jid=conv.metadata.get('jid'))
                    res = wa.send_text(conv.customer_phone, text,
                                       jid=conv.metadata.get('jid'))
                    if res.get('success'):
                        from apps.chatbot.models import Message
                        Message.objects.create(conversation=conv, role='assistant',
                                               content=text)
                conv.metadata['handoff_customer_told'] = True
                changed = True
                customer_msgs += 1

            if changed and not dry:
                conv.metadata['handoff_pings'] = done
                conv.save(update_fields=['metadata'])

        if not quiet:
            self.stdout.write(self.style.SUCCESS(
                f"Wanaosubiri: {waiting.count()} · kumbusho {owner_pings} · "
                f"jumbe kwa wateja {customer_msgs}"))

    # ──────────────────────────────────────────────────────────

    def _owner_text(self, conv, mins, level):
        who = conv.customer_name or conv.wa_contact_name or 'Mteja'
        dur = f"dakika {mins}" if mins < 60 else f"saa {mins // 60}"

        if level >= 240:
            head = "🔴 *Mteja amesubiri muda mrefu sana*"
            tail = ("Mteja aliyesubiri saa nne mara nyingi amekwisha ondoka. "
                    "Hii ni taarifa ya mwisho kuhusu mazungumzo haya.")
        elif level >= 60:
            head = "🟠 *Mteja bado anasubiri*"
            tail = "Nimemwambia bado unamtafutia, na nimempa namba yako."
        else:
            head = "⏰ *Mteja anasubiri*"
            tail = "Bot imesimama kwa mazungumzo haya."

        ident = conv.customer_phone or ''
        contact = ('fungua chat kwenye WhatsApp ya biashara'
                   if len(ident) >= 15 else ident)

        last = conv.messages.filter(role='user').order_by('-created_at').first()

        lines = [head, "", f"*{who}* — {contact}", f"Amesubiri {dur}", ""]
        if last:
            lines += [f"_Aliandika:_ {(last.content or '')[:150]}", ""]
        lines += [tail, "", f"Ukimaliza: `endelea {conv.customer_phone}`"]
        return "\n".join(lines)

    def _customer_text(self, bot):
        phone = (bot.whatsapp_number or bot.owner_whatsapp or '').strip()
        base = ("Samahani kwa kuchelewa. Bado tunakutafutia mtu wa kukusaidia — "
                "ujumbe wako haujasahaulika.")
        if phone:
            return f"{base}\n\nUkipenda kuharakisha, unaweza kutupigia {phone} moja kwa moja."
        return base
