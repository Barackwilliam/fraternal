import os, sys
try:
    import polib
except ImportError:
    print("Fanya: pip install polib")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALE_DIR = os.path.join(BASE_DIR, 'locale')

for lang in os.listdir(LOCALE_DIR):
    po_path = os.path.join(LOCALE_DIR, lang, 'LC_MESSAGES', 'django.po')
    mo_path = os.path.join(LOCALE_DIR, lang, 'LC_MESSAGES', 'django.mo')
    if not os.path.exists(po_path):
        continue
    try:
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)
        print(f"  [{lang}] OK — maneno {len(po.translated_entries())} yamekompiliwa")
    except Exception as e:
        print(f"  [{lang}] ERROR — {e}")