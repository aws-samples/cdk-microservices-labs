import json
import boto3
import cfnresponse
from botocore.exceptions import ClientError
import time

s3 = boto3.resource('s3')
ddb_client = boto3.client('dynamodb')

def create(properties, physical_id):
    print("Create Event and Properties: {}".format(json.dumps(properties)))
    
    print('Begin init dynamodb table data!')
    owner_request = {}
    
    table = properties["DynamoDBTable"]
    
    print('Import owner table data!')

    with open('owner.json', 'r') as owner_body:
      owner_request[table] = json.load(owner_body)['test_owner']
    
    ddb_client.batch_write_item(RequestItems=owner_request)

    return cfnresponse.SUCCESS, None
    
def update(properties, physical_id):
    return create(properties, physical_id)

def delete(properties, physical_id):
    return cfnresponse.SUCCESS, physical_id

def handler(event, context):
    print ("Received event: {}".format(json.dumps(event)))

    status = cfnresponse.FAILED
    new_physical_id = None

    try:
      properties = event.get('ResourceProperties')
      physical_id = event.get('PhysicalResourceId')
    
      status, new_physical_id = {
        'Create': create,
        'Update': update,
        'Delete': delete
      }.get(event['RequestType'], lambda x, y: (cfnresponse.FAILED, None))(properties, physical_id)
    except Exception as e:
      print ("Exception: {}".format(e))
      status = cfnresponse.FAILED
    finally:
      cfnresponse.send(event, context, status, {}, new_physical_id)