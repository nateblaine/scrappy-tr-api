#!/usr/bin/env python3
import json
import argparse
import sys
import re
from decimal import Decimal

def parse_args():
    parser = argparse.ArgumentParser(
        description="Refine combinedItems.json by handling 'crafting' → 'craftableUsing' and normalizing amounts"
    )
    parser.add_argument('-i', '--input',  default='combinedItems.json')
    parser.add_argument('-o', '--output', default='combined_refined.json')
    return parser.parse_args()

def slugify(s):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', s.lower())).strip('_')

def parse_used_for_crafting(val):
    items = []
    if isinstance(val, list):
        for item in val:
            if isinstance(item, str):
                items.append(item.replace('\u00a0',' ').strip())
    elif isinstance(val, str):
        s = val.replace('\\xa0',' ').replace('\u00a0',' ')
        found = re.findall(r"'([^']+)'", s)
        for item in found:
            items.append(item.strip())
    return items

def convert_amounts(list_field):
    new_list = []
    for elem in list_field:
        amt = elem.get('amount')
        if isinstance(amt, str) and amt.isdigit():
            elem['amount'] = int(amt)
        elif isinstance(amt, float):
            elem['amount'] = int(amt)
        new_list.append(elem)
    return new_list

def transform_list(lst):
    out = []
    for entry in lst:
        name = entry.get('loot_name','').replace('\u00a0',' ').strip()
        out.append({
            'amount': int(entry.get('amount', 0)),
            'itemName': name,
            'itemId': slugify(name)
        })
    return out

def main():
    args = parse_args()
    try:
        items = json.load(open(args.input, encoding='utf-8'))
    except Exception as e:
        print(f"Error loading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    # Build id→name for arc-derived crafting
    id_to_name = {it['id']: it['name'] for it in items if 'id' in it and 'name' in it}
    missing_ids = set()
    refined = []

    for it in items:
        entry = dict(it)
        crafting = entry.get('crafting')             # original arc crafting map
        cu = entry.get('craftableUsing', [])
        has_nonempty_cu = isinstance(cu, list) and len(cu) > 0

        if crafting is not None:
            # Regenerate whenever craftableUsing is missing or empty
            if not has_nonempty_cu:
                new_cu = []
                for cid, amt in crafting.items():
                    name = id_to_name.get(cid, '')
                    if not name:
                        missing_ids.add(cid)
                    new_cu.append({
                        'amount': int(amt) if isinstance(amt, (int,str)) and str(amt).isdigit() else amt,
                        'itemName': name,
                        'itemId': cid
                    })
                entry['craftableUsing'] = new_cu
                entry['craftable'] = True
            # drop the old key
            entry.pop('crafting', None)

        # Normalize any existing lists
        if 'craftableUsing' in entry:
            entry['craftableUsing'] = convert_amounts(entry['craftableUsing'])
        if 'recyclesInto' in entry:
            entry['recyclesInto'] = convert_amounts(entry['recyclesInto'])
        if 'usedForCrafting' in entry:
            entry['usedForCrafting'] = parse_used_for_crafting(entry['usedForCrafting'])

        refined.append(entry)

    if missing_ids:
        print("Warning, unmatched crafting IDs:", missing_ids, file=sys.stderr)

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(refined, f, indent=2, ensure_ascii=False)
        print(f"✅ Wrote {len(refined)} items to {args.output}")
    except Exception as e:
        print(f"Error writing {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__=='__main__':
    main()

