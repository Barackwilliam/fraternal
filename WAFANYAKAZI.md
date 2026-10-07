# Timu ya AI ya JamiiTek

Wafanyakazi watano wa AI wanaofanya kazi ndani ya JamiiTek, kwa data halisi ya
biashara. Panel yao: **/manage/wafanyakazi/** (menyu → *Timu ya AI*).

| Mfanyakazi | Kazi yake | Anasoma |
|---|---|---|
| 👔 **William** — Kiongozi mkuu | Anawakumbusha kazi zilizokwama (zaidi ya siku 2), anakutumia mpango wa asubuhi (saa 1) na ripoti ya jioni (saa 12) | Kazi za timu nzima |
| 💬 **Ibrahimu** — Mhudumu wa wateja | Wateja wanaosubiri binadamu, maswali ambayo bot haikujua (anaandaa jibu; ukikubali linakuwa FAQ), wateja wenye nia ya kununua → anampa Selvester | JamiiBot ya JamiiTek |
| 🎯 **Selvester** — Afisa mauzo | Ufuatiliaji wa leads, majibu ya fomu ya mawasiliano, malipo yaliyoachwa njiani, tovuti za builder ambazo hazijachapishwa | `/proposals/`, Contact, Pesapal, builder |
| 📣 **Grace** — Afisa masoko | Post moja kwa siku ya mitandao ya kijamii (blog → template → huduma) | Blog, templates, huduma |
| 💰 **Diana** — Fedha na ofisi | Ukumbusho wa invoice zilizochelewa/zinazokaribia, malipo ya JamiiBot ya kuthibitisha, mapato ya wiki | Invoice, Pesapal, malipo ya bot |

## Sheria ya uhuru

* Kugundua kazi, kupanga kipaumbele, kukumbusha na kuandaa rasimu → **wanafanya wenyewe**.
* Chochote kinachomfikia mteja (email, WhatsApp, jibu jipya la bot) → **kinasubiri idhini yako**:
  kwenye panel (unaweza kuhariri rasimu kwanza) au kwa *OK code* kupitia wILife.
* Grace hachapishi mwenyewe (hakuna API ya mitandao bado): post inakuja kwenye ripoti ya asubuhi
  tayari kunakiliwa, kisha unabonyeza *Nimechapisha*.

## Wanafanya kazi lini

Kila dakika 30 kupitia `DailyTasksMiddleware` (mtu anapotembelea tovuti). Render free inalala,
kwa hiyo **weka cron-job.org** iite kila dakika 30:

    https://www.jamiitek.com/tasks/wafanyakazi/?token=TASKS_TOKEN

Kwa mkono: kitufe *Endesha sasa* kwenye panel, au `python manage.py wafanyakazi [--ripoti asubuhi]`.

## Kuunganisha na wILife

Weka kwenye Render ya **JamiiTek**:

    WORKERS_API_TOKEN=<siri ndefu>
    WILIFE_URL=https://www.wlife.online

Weka kwenye Render ya **wILife**:

    JAMIITEK_URL=https://www.jamiitek.com
    JAMIITEK_TOKEN=<siri ileile>

Baada ya hapo:

* Ripoti za William zinakufikia kupitia wILife (WhatsApp/email zenye muundo wa wILife).
* Kila rasimu ya kutuma kwa mteja inakuja na *OK 1234* / *NO 1234* — ukijibu, wILife inaiambia
  JamiiTek itume au iache.
* Ukimuuliza wILife "timu ya JamiiTek iko vipi?" inasoma hali ya timu moja kwa moja.

API (header `X-Workers-Token`):

| Njia | Kazi |
|---|---|
| `GET /wafanyakazi/api/hali/` | hali ya timu, zinazosubiri idhini, ripoti ya mwisho |
| `POST /wafanyakazi/api/kazi/<id>/idhinisha/` | tuma rasimu (body hiari: `{"draft": "..."}`) |
| `POST /wafanyakazi/api/kazi/<id>/kataa/` | achana nayo |
| `POST /wafanyakazi/api/endesha/` | endesha timu sasa (`{"ripoti": "asubuhi"}` hiari) |
