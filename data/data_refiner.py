#!/usr/bin/env python3
import json
import argparse
import sys
import re

def parse_args():
    parser = argparse.ArgumentParser(
        description="Refine combinedItems.json by handling 'crafting' -> 'craftableUsing' and normalizing amounts"
    )
    parser.add_argument(
        '-i', '--input', default='combinedItems.json',
        help='Input JSON file with combined items'
    )
    parser.add_argument(
        '-o', '--output', default='combined_refined.json',
        help='Output JSON file for refined items'
    )
    return parser.parse_args()

def slugify(s):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', s.lower())).strip('_')

def parse_used_for_crafting(val):
    """
    Normalize used_for_crafting to list of strings.
    """
    items = []
    if isinstance(val, list):
        for item in val:
            if isinstance(item, str):
                items.append(item.replace('\u00a0',' ').strip())
    elif isinstance(val, str):
        s = val.replace('\\xa0',' ').replace('\u00a0',' ')
        found = re.findall(r"'([^']+)'", s)
        for item in found:
            items.append(item.replace('\u00a0',' ').strip())
    return items

def convert_amounts(list_field):
    """
    Convert 'amount' in list of dicts from string to int.
    """
    new_list = []
    for elem in list_field:
        amt = elem.get('amount', elem.get('amount'))
        # convert if it's a string that looks like a number
        try:
            elem['amount'] = int(amt)
        except (ValueError, TypeError):
            pass
        new_list.append(elem)
    return new_list

def main():
    args = parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except Exception as e:
        print(f"Error loading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    # Map id -> name
    id_to_name = {it['id']: it['name'] for it in items if 'id' in it and 'name' in it}

    missing_ids = set()
    refined = []

    for it in items:
        entry = dict(it)
        crafting = entry.get('crafting')
        has_cu = 'craftableUsing' in entry

        if crafting is not None:
            if has_cu:
                entry.pop('crafting', None)
            else:
                cu = []
                for cid, amt in crafting.items():
                    name = id_to_name.get(cid, '')
                    if not name:
                        missing_ids.add(cid)
                    cu.append({
                        'amount': int(amt) if isinstance(amt, (int, float, str)) and str(amt).isdigit() else amt,
                        'itemName': name,
                        'itemId': cid
                    })
                entry['craftableUsing'] = cu
                entry['craftable'] = True
                entry.pop('crafting', None)

        # Normalize amounts in craftableUsing and recyclesInto
        if 'craftableUsing' in entry:
            entry['craftableUsing'] = convert_amounts(entry['craftableUsing'])
        if 'recyclesInto' in entry:
            entry['recyclesInto'] = convert_amounts(entry['recyclesInto'])

        # Parse usedForCrafting if present
        if 'usedForCrafting' in entry:
            entry['usedForCrafting'] = parse_used_for_crafting(entry['usedForCrafting'])

        refined.append(entry)

    if missing_ids:
        print("Warning: the following ingredient IDs had no matching name:", list(missing_ids), file=sys.stderr)

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(refined, f, indent=2, ensure_ascii=False)
        print(f"✅ Wrote {len(refined)} items to {args.output}")
    except Exception as e:
        print(f"Error writing {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
