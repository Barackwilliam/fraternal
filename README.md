# 🏪 Mudandaza POS — Simamia Biashara Yako Kwa Nguvu

## Jinsi ya Kuanza
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Akaunti za Demo
| Mtumiaji | Nywila | Aina |
|---|---|---|
| `admin` | `admin123` | Super Admin |
| `demo_duka` | `demo123` | Demo Store (na bidhaa 6) |

- `/` — Homepage
- `/accounts/login/` — Ingia
- `/accounts/register/` — Jiandikishe
- `/store/dashboard/` — Dashibodi
- `/store/pos/` — Mauzo (POS)
- `/superadmin/` — Super Admin Panel

## Audit Results: 100% ✅
- Templates: 22/22 OK
- URLs: 24/24 OK  
- Python files: 35/35 OK
- Languages: 4/4 OK
- Django check: 0 issues
