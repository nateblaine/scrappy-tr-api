#!/usr/bin/env python3
import json
import argparse
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

def parse_args():
    parser = argparse.ArgumentParser(
        description="Upload JSON items to a DynamoDB table, converting floats to Decimal."
    )
    parser.add_argument(
        "--table", "-t",
        default="ScrappyTheRooster-arcraiders-data",
        help="DynamoDB table name"
    )
    parser.add_argument(
        "--file", "-f",
        default="combined_refined.json",
        help="Path to JSON file containing an array of items"
    )
    return parser.parse_args()

def sanitize_value(v):
    """Convert float to Decimal and recurse through lists/dicts."""
    if isinstance(v, float):
        return Decimal(str(v))
    if isinstance(v, dict):
        return {k: sanitize_value(val) for k, val in v.items()}
    if isinstance(v, list):
        return [sanitize_value(val) for val in v]
    return v

def sanitize_item(item):
    """Sanitize all values in the item."""
    return {k: sanitize_value(v) for k, v in item.items()}

def upload_items(table_name: str, file_path: str):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    with open(file_path, 'r', encoding='utf-8') as f:
        items = json.load(f)

    count = 0
    with table.batch_writer() as batch:
        for item in items:
            sanitized = sanitize_item(item)
            try:
                batch.put_item(Item=sanitized)
                count += 1
            except ClientError as e:
                print(f"❌ Failed to upload id={item.get('id')}: {e.response['Error']['Message']}")

    print(f"✅ Uploaded {count} items to table '{table_name}'")

if __name__ == "__main__":
    args = parse_args()
    upload_items(args.table, args.file)
