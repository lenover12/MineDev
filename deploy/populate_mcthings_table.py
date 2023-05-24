from decimal import Decimal
import json
import boto3

dynamodb = boto3.resource('dynamodb')

def load_mcthings(mcthings, dynamodb):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
  
    table = dynamodb.Table('mcthings')
    for thing in mcthings:

        thing['title_f'] = thing['title']
        
        # Convert title to lowercase
        thing['title'] = thing['title'].lower()

        # Add other fields to mcthings table
        print("Adding thing:", thing['title'])
        table.put_item(Item=thing)

if __name__ == '__main__':
    with open("minecraft_things.json") as minecraft_things:
        mcthings = json.load(minecraft_things, parse_float=Decimal)
    load_mcthings(mcthings, dynamodb)