#!/usr/bin/env python3
import json
import argparse
import re

def slugify(s):
    """Lowercase, replace non-alphanum with underscore, collapse underscores."""
    return re.sub(r'_+', '_',
           re.sub(r'[^a-z0-9]+', '_', s.lower())
           ).strip('_')

def parse_args():
    p = argparse.ArgumentParser(
        description="Combine arcraiders_data_items.json + all_loot.json → combinedItems.json"
    )
    p.add_argument('-a','--arc-file',  default='arcraiders_data_items.json',
                   help="Path to Arc Raiders data items JSON")
    p.add_argument('-l','--loot-file', default='all_loot.json',
                   help="Path to all_loot JSON file")
    p.add_argument('-o','--output',    default='combinedItems.json',
                   help="Path for output combined JSON")
    return p.parse_args()

def parse_used_for_crafting(val):
    """
    Normalize used_for_crafting field:
    - If list, replace non-breaking spaces and strip.
    - If string (e.g. "{'A', 'B'}"), extract items.
    """
    items = []
    if isinstance(val, list):
        for item in val:
            if isinstance(item, str):
                items.append(item.replace('\u00a0',' ').strip())
    elif isinstance(val, str):
        # Replace literal escapes and unicode non-breaking spaces
        s = val.replace('\\xa0',' ').replace('\u00a0',' ')
        # Extract content inside single quotes
        found = re.findall(r"'([^']+)'", s)
        for item in found:
            items.append(item.replace('\u00a0',' ').strip())
    return items

def transform_list(lst):
    """
    lst: list of { 'amount': str, 'loot_name': str }
    returns list of { 'amount', 'itemName', 'itemId' }
    """
    out = []
    for entry in lst:
        name = entry.get('loot_name','').replace('\u00a0',' ').strip()
        out.append({
            'amount': entry.get('amount',''),
            'itemName': name,
            'itemId': slugify(name)
        })
    return out

def main():
    args = parse_args()

    arc_items = json.load(open(args.arc_file,  encoding='utf-8'))
    loot_items = json.load(open(args.loot_file, encoding='utf-8'))

    loot_map = { L['loot_name']: L for L in loot_items }
    unmatched_loot = set(loot_map.keys())
    unmatched_arc = []

    combined = []
    for arc in arc_items:
        name = arc.get('name')
        loot = loot_map.get(name)
        if not loot:
            unmatched_arc.append(name)
            craftable = False
            craftable_using = []
            recycles_into = []
            used_for = []
        else:
            unmatched_loot.discard(name)
            craftable = loot.get('craftable', False)
            craftable_using = transform_list(loot.get('craftable_using', []))
            recycles_into   = transform_list(loot.get('recycles_into', []))
            used_for        = parse_used_for_crafting(loot.get('used_for_crafting', []))
        combined.append({
            **arc,  # includes id, name, description, type, imageFilename, etc.
            'craftable':       craftable,
            'craftableUsing':  craftable_using,
            'recyclesInto':    recycles_into,
            'usedForCrafting': used_for
        })

    if unmatched_arc:
        print("Arc items with no loot match:", unmatched_arc)
    if unmatched_loot:
        print("Loot entries with no arc match:", list(unmatched_loot))

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"✅ Wrote {len(combined)} items to {args.output}")

if __name__=='__main__':
    main()

