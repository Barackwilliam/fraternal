# JamiiTek — tayari kwa DEBUG=False

Kila kitu kwenye zip hii kimejaribiwa kwa `DEBUG=False` halisi, si kwa nadharia.

## Kilichofanyika

**1. Picha 22 zilizokosekana.** Zilikuwa zinaitwa na `index.html` lakini
hazikuwepo. Kwa `CompressedManifestStaticFilesStorage`, faili moja
iliyokosekana si picha tupu — ni `ValueError` inayoangusha ukurasa mzima.
Nimeweka placeholders zenye brand yako kwenye vipimo sahihi. Zibadilishe
na picha halisi wakati wowote; majina na ukubwa vibaki vilevile.

**2. `favicon.ico`.** Ilikuwa `apps/static/images/favicon.ico` lakini
templates zinaiita kama `{% static 'favicon.ico' %}`. Nimeiweka pia kwenye
mzizi wa static.

**3. Logo.** `logo.png` ilikuwa na background ya navy — ilionekana kama
kisanduku cheusi kwenye header nyeupe. Nimeondoa background (sasa ni
transparent) na kutengeneza `logo-white.png` iliyoangazwa kwa footer ya navy.

**4. `apps/static/lib/` na `apps/static/mail/` zimeondolewa** (912 KB).
Ni mabaki ya theme ya zamani; hakuna template inayoziita. Muhimu zaidi:
`lib/lightbox/js/lightbox.min.js` ilikuwa inaita `.map` isiyokuwepo, na
manifest inasoma **ndani ya JS na CSS** pia — hiyo peke yake ilikuwa
inaangusha `collectstatic` kwenye Render.

**5. `img/carousel-1.jpg` na `img/quote.png`.** `css/style.css` (inayotumika
na blog, portfolio, single) inaziita kwenye `url()`. Hazikuwepo, kwa hiyo
manifest ilikuwa inashindwa. Nimeziweka.

**6. `DEBUG` sasa inasoma environment:**

```python
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

Default ni `False`, kwa hiyo production iko salama kwa muundo, si kwa
kukumbuka. Kwenye kompyuta yako, `.env` iwe na `DEBUG=True`.

**7. Bug ya migrations.** Hii ilikuwa imejificha kabisa. Kwenye database
mpya, `migrate` ilikuwa inashindwa:

```
duplicate column name: facebook_link
duplicate column name: linkedin_link
```

Sababu: `0003_team` na `0004_team` zinaunda Team pamoja na fields hizo,
lakini `0002_team_facebook...` na `0005_add_linkedin_to_team` zinajaribu
kuziongeza tena. Django ilikuwa huru kuendesha `0003_team` kwanza kwa
sababu haikutegemea `0002_team_facebook`.

Database yako ya sasa haikuathirika kwa sababu migrations zilishaandikwa.
Lakini Render ikitengeneza database mpya, au ukirudisha backup, deploy
ingekufa. Nimeziacha faili zote mbili zikiwa na `operations = []` — Django
inarekodi jina la migration pekee, kwa hiyo databases zilizopo hazibadiliki
na mpya zinafanya kazi.

## Kilichojaribiwa

```
check_static.py                  0 missing
collectstatic + manifest         imefanikiwa
migrate kwenye database mpya     imefanikiwa (tables 32)
kurasa 11 kwa DEBUG=False        hakuna 500 hata moja
```

Kurasa zilizojaribiwa: `/`, `/service/`, `/About/`, `/contact/`,
`/portal/login/`, `/portal/register/`, `/get-started/`, `/templates/`,
`/blog/`, URL isiyokuwepo (404 mpya), `/offline.html`, `/sw.js`.

## Kabla ya kuendesha

`.env` **haiko** kwenye zip hii kwa makusudi. Tumia yako ya sasa, au nakili
`.env.example`. Kwa kompyuta yako:

```
DEBUG=True
```

Kwenye Render, `DEBUG` iachwe bila kuwekwa au iwe `False`.

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py runserver
```

Kujaribu jinsi production itakavyokuwa:

```powershell
# .env: DEBUG=False
python manage.py collectstatic --no-input
python manage.py runserver --insecure
```

## Kabla ya kila deploy

```powershell
python check_static.py
```

Ikisema *usi-deploy bado*, weka faili zilizotajwa kwanza. Script inasoma
templates pekee — haisomi ndani ya CSS na JS. Kwa hiyo endesha pia
`collectstatic` kwenye kompyuta yako kabla ya kutuma; ndiyo inayokamata
`url()` iliyovunjika.

## Bado linahitajika

`SECRET_KEY` ya zamani iko kwenye git history. Itengeneze mpya:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Iweke kwenye Render kama environment variable. Watumiaji watatakiwa kuingia
upya — hiyo ni sawa na inatakiwa.

Pia `.env` bado inafuatiliwa na git licha ya `.gitignore`:

```powershell
git rm --cached .env
```
