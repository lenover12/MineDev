import boto3

dynamodb = boto3.resource('dynamodb')

#>1.2
# Create the DynamoDB music table
def create_mcthings_table(dynamodb=None):
  if not dynamodb:
      dynamodb = boto3.resource('dynamodb')

  table = dynamodb.create_table(
    TableName='mcthings',
    KeySchema=[
      {
      'AttributeName': 'title',
      'KeyType': 'HASH' #partician key
      }
    ],
    AttributeDefinitions=[
      {
      'AttributeName': 'title',
      'AttributeType': 'S' #string
      }
    ],
    ProvisionedThroughput={
      'ReadCapacityUnits': 10,
      'WriteCapacityUnits': 10
    }
  )
  return table

#run the table creator
if __name__ == '__main__':
  mcthings_table = create_mcthings_table(dynamodb)
  print("Table status: ", mcthings_table.table_status)