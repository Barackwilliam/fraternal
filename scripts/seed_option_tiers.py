#!/usr/bin/env python3
"""
scripts/seed_option_tiers.py

Inaongeza daraja (tier) kwenye options za website_types/*.json.

FORMAT:
    kabla :  "User Registration & Profiles | 15000"
    baada :  "User Registration & Profiles | 15000 | A"

DARAJA:
    A = Msingi     (kila kifurushi kinacho)
    B = Biashara   (Kifurushi B na C)
    C = Premium    (Kifurushi C pekee)

Vifurushi ni CUMULATIVE: B = A + B,  C = A + B + C.

MUUNDO WA KUGAWA (heuristic):
    Ndani ya kila swali, options zinapangwa kwa bei:
      · bei 0            -> A
      · 40% ya chini     -> A
      · 35% inayofuata   -> B
      · 25% ya juu       -> C
    Hii ni ANZA TU. Baada ya kukimbiza, pitia files na urekebishe
    kwa mkono pale unapoona kipengele kimewekwa daraja lisilofaa.

MATUMIZI:
    python scripts/seed_option_tiers.py --dry-run     # onyesha bila kubadilisha
    python scripts/seed_option_tiers.py               # badilisha kweli
    python scripts/seed_option_tiers.py --file ecommerce.json
"""

import argparse
import json
import math
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TYPES_DIR = BASE_DIR / 'website_types'

SHARE_A = 0.40
SHARE_B = 0.35


def parse_option(raw):
    """Rudisha (jina, bei, daraja_au_None)."""
    parts = [p.strip() for p in str(raw).split('|')]

    if len(parts) >= 3 and parts[-1].upper() in ('A', 'B', 'C'):
        tier = parts[-1].upper()
        price_part = parts[-2]
        name = '|'.join(parts[:-2]).strip()
    elif len(parts) >= 2:
        tier = None
        price_part = parts[-1]
        name = '|'.join(parts[:-1]).strip()
    else:
        return parts[0], 0, None

    digits = ''.join(ch for ch in price_part if ch.isdigit())
    price = int(digits) if digits else 0
    return name, price, tier


def assign_tiers(options):
    """Rudisha list mpya ya options zenye daraja."""
    parsed = [parse_option(o) for o in options]

    # Kama zote tayari zina daraja, usiguse
    if all(t is not None for _, _, t in parsed):
        return options, 0

    priced = sorted(
        [(i, p) for i, (_, p, _) in enumerate(parsed) if p > 0],
        key=lambda x: x[1]
    )

    n = len(priced)
    cut_a = math.ceil(n * SHARE_A)
    cut_b = math.ceil(n * (SHARE_A + SHARE_B))

    tier_by_index = {}
    for rank, (idx, _) in enumerate(priced):
        if rank < cut_a:
            tier_by_index[idx] = 'A'
        elif rank < cut_b:
            tier_by_index[idx] = 'B'
        else:
            tier_by_index[idx] = 'C'

    out, changed = [], 0
    for i, (name, price, existing) in enumerate(parsed):
        tier = existing or tier_by_index.get(i, 'A')   # bei 0 -> A
        out.append(f'{name} | {price} | {tier}')
        if existing is None:
            changed += 1

    return out, changed


def process(path, dry_run):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f'  !! {path.name}: JSON haijaandikwa vizuri ({e}) — imerukwa')
        return 0
    except Exception as e:
        print(f'  !! {path.name}: {e} — imerukwa')
        return 0

    if not isinstance(data, dict):
        print(f'  -- {path.name}: si object — imerukwa')
        return 0

    total_changed = 0
    for key, field in data.items():
        if not isinstance(field, dict):
            continue
        if field.get('type') != 'checkbox':
            continue
        options = field.get('options')
        if not isinstance(options, list) or not options:
            continue

        new_options, changed = assign_tiers(options)
        if changed:
            field['options'] = new_options
            total_changed += changed
            if dry_run:
                print(f'     {key}:')
                for o in new_options:
                    print(f'        {o}')

    if total_changed and not dry_run:
        backup = path.with_suffix('.json.bak')
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + '\n',
            encoding='utf-8'
        )

    return total_changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true',
                    help='Onyesha mabadiliko bila kuandika')
    ap.add_argument('--file', help='Fanyia file moja tu, mfano ecommerce.json')
    args = ap.parse_args()

    if not TYPES_DIR.is_dir():
        print(f'Folder haipatikani: {TYPES_DIR}')
        sys.exit(1)

    files = ([TYPES_DIR / args.file] if args.file
             else sorted(TYPES_DIR.glob('*.json')))

    grand = 0
    for path in files:
        if not path.is_file():
            print(f'  !! {path.name}: haipatikani')
            continue
        print(f'\n  {path.name}')
        n = process(path, args.dry_run)
        grand += n
        print(f'     -> options {n} zimepewa daraja')

    print(f'\n{"[DRY RUN] " if args.dry_run else ""}Jumla: {grand} options')
    if not args.dry_run and grand:
        print('Backup za .json.bak zimehifadhiwa kando ya kila file.')


if __name__ == '__main__':
    main()