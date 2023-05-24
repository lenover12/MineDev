import random
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'mcthings'

def lambda_handler(event, context):
    operation = event['httpMethod']
    if operation == 'GET':
        if event['path'] == '/random-item':
            return get_random_item()
    elif operation == 'POST':
        if event['path'] == '/block-information':
            search_query = event['body'].get('search_query', '')
            return search_item(search_query)
    return {
        'statusCode': 404,
        'body': 'Not Found'
    }

def get_random_item():
    table = dynamodb.Table(table_name)
    response = table.scan(Select='COUNT')
    total_items = response['Count']
    random_index = random.randint(0, total_items - 1)
    response = table.scan(Limit=1, ExclusiveStartKey={'title': f'item-{random_index}'})
    random_item = response['Items'][0] if 'Items' in response else None

    if random_item:
        return {
            'statusCode': 200,
            'body': random_item
        }
    else:
        return {
            'statusCode': 404,
            'body': 'No random item found'
        }

def search_item(title):
    table = dynamodb.Table(table_name)
    response = table.scan(FilterExpression=boto3.dynamodb.conditions.Key('title').eq(title))
    search_results = response['Items']

    if search_results:
        return {
            'statusCode': 200,
            'body': search_results[0]  # Return the first item
        }
    else:
        return {
            'statusCode': 404,
            'body': 'No matching items found'
        }
