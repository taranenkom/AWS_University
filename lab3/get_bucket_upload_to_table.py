import boto3
import pandas as pd
import io
from decimal import Decimal

bucket_name = 'lab2-inmyuni'
csv_key = 'exchange_2022.csv'
dynamodb_table = 'money_money'

s3 = boto3.client('s3')
response = s3.get_object(Bucket=bucket_name, Key=csv_key)

csv_content = response['Body'].read().decode('utf-8')
df = pd.read_csv(io.StringIO(csv_content))

if 'date' in df.columns:  # cause i had named the column wrong
    df = df.rename(columns={'date': 'day'})

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)

print("Progress:")
for index, row in df.iterrows():
    item = {
        'day': row['day'],
        'USD': Decimal(str(row['USD'])),
        'EUR': Decimal(str(row['EUR']))
    }
    table.put_item(Item=item)  # adding to the DYNAMODB table
    print(f"{(index + 1) / len(df) * 100:.2f}% ({index + 1}/{len(df)})")

# ===========================
# SEARCHING AND DELETING
# ===========================

search_day = '2022-01-05'

print(f"\nSearching for day = {search_day}")
response = table.get_item(Key={'day': search_day})

item = response.get('Item')
if item:
    print("Found item:", item)
    print("Deleting...")
    table.delete_item(Key={'day': search_day})
    print("Deleted")
else:
    print("Item not found")
