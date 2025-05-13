# src/api_handler.py

import os
import json
import boto3
import decimal

# Grab the table name from env (or default)
TABLE_NAME = os.environ.get('DDB_TABLE', 'ScrappyTheRooster-Loot')

# Init Dynamo resource & table
ddb = boto3.resource('dynamodb')
table = ddb.Table(TABLE_NAME)

def _to_native(val):
    """
    Convert Decimal -> int/float, set -> list, leave other types alone.
    """
    if isinstance(val, decimal.Decimal):
        # integer?
        if val % 1 == 0:
            return int(val)
        return float(val)
    if isinstance(val, set):
        return list(val)
    return val

def lambda_handler(event, context):
    # Extract and normalize the loot name
    loot = event['pathParameters']['item'].strip()

    # Fetch the item
    resp = table.get_item(Key={'loot_name': loot})
    item = resp.get('Item')
    if not item:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Item "{loot}" not found'})
        }

    # Branch on the incoming path
    if event['rawPath'].startswith('/sell'):
        body = {
            'loot_name':       loot,
            'description':     item.get('description'),
            'sell_value':      _to_native(item.get('sell_value')),
            'rarity':          item.get('rarity')
        }
    else:  # /recycle
        recs = item.get('recycles_into', [])
        # Each entry is a dict like {'loot_name': 'ARC Alloys', 'amount': Decimal('7')}
        converted = [
            {
                'loot_name': entry.get('loot_name'),
                'amount':    _to_native(entry.get('amount'))
            }
            for entry in recs
        ]
        body = {
            'loot_name':       loot,
            'recycles_into':   converted
        }

    return {
        'statusCode': 200,
        'body':       json.dumps(body)
    }
