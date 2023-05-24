import boto3

dynamodb = boto3.resource('dynamodb')

def create_share_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='share',
        KeySchema=[
            {
                'AttributeName': 'ID',
                'KeyType': 'HASH'  # partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ID',
                'AttributeType': 'N'  # number
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

# Run the table creator
if __name__ == '__main__':
    share_table = create_share_table(dynamodb)
    print("Table status:", share_table.table_status)
