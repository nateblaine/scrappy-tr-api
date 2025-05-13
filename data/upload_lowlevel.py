#!/usr/bin/env python3
import boto3, json, argparse
from itertools import islice

def chunked(iterable, size=25):
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            return
        yield batch

def clean_item(item):
    """
    Remove any empty-set (SS/NS) or empty-list (L) attributes,
    since DynamoDB doesn't allow them.
    """
    cleaned = {}
    for k, v in item.items():
        # Only consider low-level types
        if isinstance(v, dict):
            # if it's an empty set or list, skip it
            if 'SS' in v and v['SS'] == []: continue
            if 'NS' in v and v['NS'] == []: continue
            if 'L'  in v and v['L']  == []: continue
            # Convert empty numeric to "0"
            if 'N' in v and v['N'] == "":
                v['N'] = "0"
        cleaned[k] = v
    return cleaned

def upload_lowlevel(table_name, items, test=False):
    client = boto3.client('dynamodb')
    # Clean all items up front
    cleaned_items = [clean_item(i) for i in items]

    if test:
        print(">>> Test put_item for:")
        print(json.dumps(cleaned_items[0], indent=2))
        client.put_item(TableName=table_name, Item=cleaned_items[0])
        print("✅ Test succeeded")
    else:
        for batch in chunked(cleaned_items, 25):
            request_items = {
                table_name: [
                    { "PutRequest": { "Item": item }} for item in batch
                ]
            }
            resp = client.batch_write_item(RequestItems=request_items)
            unprocessed = resp.get("UnprocessedItems", {}).get(table_name, [])
            # retry any unprocessed
            if unprocessed:
                client.batch_write_item(RequestItems={ table_name: unprocessed })
        print(f"✅ Uploaded {len(cleaned_items)} items to {table_name}")

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-t","--table", required=True, help="DynamoDB table name")
    p.add_argument("-f","--file",  default="items.json", help="Low‑level JSON file")
    p.add_argument("--test", action="store_true", help="Only upload first item")
    args = p.parse_args()

    with open(args.file) as f:
        data = json.load(f)
    upload_lowlevel(args.table, data, test=args.test)
