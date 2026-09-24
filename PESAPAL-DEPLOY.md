# Pesapal Payments — JamiiTek (API 3.0)

Injini moja ya malipo inayotumika kwa **mfumo mzima**: chatbot subscriptions,
hosting renewals, na invoices. Sandbox kwanza, ubadilishe kuwa live kwa env moja.

## 1. Faili zilizoongezwa / kubadilishwa

**Mpya**
- `apps/pesapal_models.py` — `PesapalTransaction` (transaction ya jumla)
- `apps/pesapal_client.py` — client ya API 3.0 (token, IPN, order, status)
- `apps/pesapal_fulfill.py` — kinachotokea baada ya malipo (idempotent)
- `apps/pesapal_receipt.py` — risiti + email ya kiotomatiki (PDF ambatanisho)
- `apps/pesapal_views.py` — initiate / callback / IPN / status page
- `apps/templates/pesapal/status.html` — ukurasa wa hali ya malipo
- `apps/management/commands/pesapal_register_ipn.py` — sajili IPN
- `apps/migrations/0031_pesapaltransaction.py`

**Zilizoguswa (nyongeza tu, hakuna kilichovunjwa)**
- `jamiitek/settings.py` — config ya Pesapal
- `apps/models.py` — import ya model mpya
- `apps/urls.py` — routes za `/pay/...`
- `apps/context_processors.py` — bendera `PESAPAL_ENABLED`
- `apps/admin.py` — admin ya transactions
- `apps/chatbot/templates/chatbot/portal/billing.html` — kitufe cha Pesapal (subscription)
- `apps/templates/portal/billing.html` + `_pay_multi.html` — kitufe cha Pesapal (hosting)
- `apps/templates/docs/invoice_view.html` — kitufe cha Pesapal (invoice)

## 2. Env variables (Render / server)

```
PESAPAL_CONSUMER_KEY=xxxxxxxx
PESAPAL_CONSUMER_SECRET=xxxxxxxx
PESAPAL_ENV=sandbox            # badilisha kuwa 'live' ukiwa tayari
PESAPAL_BASE_URL=https://www.jamiitek.com   # domain halisi (kwa callback/IPN)
PESAPAL_IPN_ID=                # jaza baada ya hatua ya 4 (hiari)
PAYMENTS_OWNER_EMAIL=info@jamiitek.com   # nakala ya kila risiti (hiari)
```

- **Sandbox** consumer key/secret: pata kwenye https://developer.pesapal.com (akaunti ya majaribio).
- **Live**: badilisha `PESAPAL_ENV=live` na weka key/secret za live kutoka dashboard yako ya Pesapal.
- Malipo hayaonekani (button haitokei) mpaka key + secret ziwepo — hakuna kinachovunjika ukiacha wazi.

## 3. Migration

Inaendeshwa moja kwa moja kwenye deploy (`build.sh` ina `migrate`). Kwa mkono:

```
python manage.py migrate apps
```

## 4. Sajili IPN (mara moja)

Baada ya kuweka key/secret na `PESAPAL_BASE_URL`:

```
python manage.py pesapal_register_ipn
```

Itachapisha `ipn_id`. Weka kwenye env kama `PESAPAL_IPN_ID` (au acha — mfumo
utasajili moja kwa moja na kucache. Kuweka env ni bora zaidi kwa Render free tier
isiyoruhusu commands.)

> **Render free tier haiwezi kuendesha commands:** acha `PESAPAL_IPN_ID` wazi.
> Mfumo utasajili IPN wenyewe mara ya kwanza mtu anapolipa na kucache siku 30.

## 5. URLs

| Njia | Jina | Nani |
|------|------|------|
| `POST /pay/subscription/` | `pesapal_pay_subscription` | chatbot client |
| `POST /pay/hosting/<pk>/` | `pesapal_pay_hosting` | portal client |
| `POST /pay/invoice/<token>/` | `pesapal_pay_invoice` | umma (public) |
| `GET /pay/callback/` | `pesapal_callback` | browser redirect |
| `POST /pay/ipn/` | `pesapal_ipn` | Pesapal server |

## 6. Jinsi inavyofanya kazi

1. Mteja abonyeza **"Lipa na Pesapal"** → tunajenga `PesapalTransaction`,
   tunaanzisha order, na kumpeleka Pesapal.
2. Mteja alipa (kadi / M-Pesa / Airtel / Tigo / Halopesa).
3. Pesapal humrudisha `/pay/callback/` **na** hutuma `/pay/ipn/` (server-to-server).
4. Zote mbili huangalia hali halisi (`GetTransactionStatus`) kisha huendesha
   **fulfillment** mara **moja** tu (`fulfilled` flag + row lock):
   - **Subscription** → rekodi `SubscriptionPayment` (verified), ongeza `end_date`,
     status `active`, anzisha upya hesabu ya jumbe.
   - **Hosting** → rekodi `HostingPayment`, ongeza `hosting_end_date`, status `active`.
   - **Invoice** → `amount_paid = grand_total`, status `paid`.
5. **Risiti + email otomatiki** — baada ya fulfillment, mfumo hutengeneza
   `DevelopmentReceipt` (RCP-YYYY-NNNN), huitengenezea PDF, na kuituma kwa
   mteja kwa email; nakala (BCC) humwendea mmiliki. Idempotent — risiti moja
   kwa kila malipo. Ikishindikana (mtandao/email), malipo hayaathiriki.

## 7. Kupima (sandbox)

- Tumia namba/kadi za majaribio za Pesapal (angalia developer.pesapal.com → Testing).
- Angalia transaction kwenye admin: `/manage/... ` → **Pesapal Transactions**.
- IPN + callback zote huthibitisha; hata moja ikichelewa, nyingine itakamilisha.

## 8. Live checklist

- [ ] `PESAPAL_ENV=live`
- [ ] consumer key/secret za live
- [ ] `PESAPAL_BASE_URL` = domain halisi ya https
- [ ] `pesapal_register_ipn` imeendeshwa kwa live (au acha env wazi ili isajili yenyewe)
- [ ] Jaribu malipo halisi moja dogo kudhibitisha callback + IPN
