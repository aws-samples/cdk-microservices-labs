import json
import boto3
import cfnresponse
from botocore.exceptions import ClientError
import time

s3 = boto3.resource('s3')
ddb_client = boto3.client('dynamodb')

def create(properties, physical_id):
    print("Create Event and Properties: {}".format(json.dumps(properties)))
    
    bucket = properties['Bucket']
    print('Begin init dynamodb table data!')
    owner_request = {}
    vet_request = {}
    visit_request = {}
    
    for table in properties["DynamoDBTables"]:
      if 'Customer' in table:
        owner_tab = table
      elif 'Vet' in table:
        vet_tab = table
      else:
        visit_tab = table
    
    print('Import owner table data!')
    keep_try = True
    while keep_try:
      try:
        owner_body = s3.Object(bucket, 'data/owner.json').get()['Body']
        owner_request[owner_tab] = json.load(owner_body)['test_owner']
        ddb_client.batch_write_item(RequestItems=owner_request)
        keep_try = False
      except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
          print('Seelp 5s to wait for the owner.json to be uploaded...')
          time.sleep(5)
        else:
          raise
        
    print('Import vet table data!')   
    keep_try = True
    while keep_try:
      try:
        vet_body = s3.Object(bucket, 'data/vet.json').get()['Body']
        vet_request[vet_tab] = json.load(vet_body)['test_vet']
        ddb_client.batch_write_item(RequestItems=vet_request)
        keep_try = False
      except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
          print('Seelp 5s to wait for the vet.json to be uploaded...')
          time.sleep(5)
        else:
          raise
    
    print('Import visit table data!')
    keep_try = True
    while keep_try:
      try:
        visit_body = s3.Object(bucket, 'data/visit.json').get()['Body']
        visit_request[visit_tab] = json.load(visit_body)['test_visit']
        ddb_client.batch_write_item(RequestItems=visit_request)
        keep_try = False
      except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
          print('Seelp 5s to wait for the visit.json to be uploaded...')
          time.sleep(5)
        else:
          raise
    
    keep_try = True
    while keep_try:
      try:
        config_object = s3.Object(bucket, 'scripts/config.js')
        config_data = config_object.get()['Body'].read().decode('utf-8')
        config_data = config_data.replace("_baseUrl = ''", "_baseUrl = '{}'".format(properties["InvokeUrl"]))
        config_object.put(Body=config_data)
        keep_try = False
      except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
          print('Seelp 5s to wait for the config.js to be uploaded...')
          time.sleep(5)
        else:
          raise
    
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