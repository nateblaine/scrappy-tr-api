import boto3
import json
import argparse

def export_items(table_name, output_file):
    """
    Export all items from the specified DynamoDB table to a JSON file.
    """
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    items = []
    # Initial scan
    response = table.scan()
    items.extend(response.get('Items', []))

    # Continue scanning if more data is available (pagination)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(items, f, default=str, indent=2)

    print(f"✅ Exported {len(items)} items to '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export all DynamoDB table items to a JSON file."
    )
    parser.add_argument(
        "--table", "-t", required=True,
        help="Name of the DynamoDB table to export from"
    )
    parser.add_argument(
        "--output", "-o", default="exported_items.json",
        help="Path to the output JSON file"
    )
    args = parser.parse_args()
    export_items(args.table, args.output)
