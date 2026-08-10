
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
STATIC_DIRS = [ROOT / 'apps' / 'static']
SKIP = {'staticfiles', '.git', 'node_modules', 'venv', '.venv'}

STATIC_TAG = re.compile(r"""\{%\s*static\s+['"]([^'"]+)['"]\s*%\}""")


def templates():
    for path in ROOT.rglob('*.html'):
        if any(part in SKIP for part in path.parts):
            continue
        yield path


def main():
    refs = defaultdict(set)
    dynamic = []

    for path in templates():
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        rel = path.relative_to(ROOT)

        for name in STATIC_TAG.findall(text):
            refs[name].add(str(rel))

        # {% static something_variable %} cannot be checked from here
        for line in re.findall(r"\{%\s*static\s+([^'\"][^%]*)%\}", text):
            dynamic.append((str(rel), line.strip()))

    missing = {
        name: files for name, files in refs.items()
        if not any((d / name).exists() for d in STATIC_DIRS)
    }

    print(f'Templates scanned : {sum(1 for _ in templates())}')
    print(f'Static references : {len(refs)}')
    print(f'Missing files     : {len(missing)}')
    print()

    if missing:
        print('HAZIPO — kila moja ni 500 inayosubiri kwa DEBUG=False:\n')
        for name in sorted(missing):
            print(f'  {name}')
            for f in sorted(missing[name])[:3]:
                print(f'      <- {f}')
            print(f'      -> weka: apps/static/{name}')
            print()

    if dynamic:
        print('Zenye variable (haziwezi kukaguliwa hapa, zithibitishe mwenyewe):')
        for f, expr in dynamic[:10]:
            print(f'  {f}: {{% static {expr}%}}')
        print()

    if missing:
        print('MATOKEO: usi-deploy bado.')
        return 1

    print('MATOKEO: static zote zipo. Uko tayari kwa DEBUG=False.')
    return 0


if __name__ == '__main__':
    sys.exit(main())