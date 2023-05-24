import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('share')

def lambda_handler(event, context):
    operation = event['httpMethod']
    if operation == 'GET':
        if event['path'] == '/get_comments':
            return get_comments()
        if event['path'] == '/get_last_id':
            return get_last_id()
    elif operation == 'POST':
        if event['path'] == '/store_comment':
            return store_comment()
    return {
        'statusCode': 404,
        'body': 'Not Found'
    }

def get_comments():
    # Scan the DynamoDB table to retrieve the last 15 comments based on the ID
    response = table.scan(
        Limit=15,
        ScanIndexForward=False,  # Sort in descending order
        KeyConditionExpression='ID >= :id',
        ExpressionAttributeValues={':id': 0},
    )

    items = response['Items']

    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }
    
def get_last_id():
    # Scan the DynamoDB table to retrieve the last item based on the ID
    response = table.scan(
        Limit=1,
        ScanIndexForward=False,  # Sort in descending order
        KeyConditionExpression='ID >= :id',
        ExpressionAttributeValues={':id': 0},
        ProjectionExpression='ID',
    )

    items = response['Items']
    if items:
        last_id = int(items[0]['ID'])
    else:
        last_id = 0

    return {
        'statusCode': 200,
        'body': json.dumps(last_id)
    }

def store_comment():
    # Retrieve the payload from the request body
    payload = json.loads(event['body'])

    # Get the last ID from the 'share' table
    last_id = get_last_id()

    # Generate a new ID by incrementing the last ID
    new_id = last_id + 1

     # Prepare the item to be stored in the table
    item = {
        'ID': new_id,
        'title': payload['title'],
        'comment': payload['comment']
    }

    # Put the item into the 'share' table
    table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': 'Comment stored successfully'
    }
