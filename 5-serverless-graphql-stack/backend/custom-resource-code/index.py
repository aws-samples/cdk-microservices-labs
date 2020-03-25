import json
import boto3
import cfnresponse
from botocore.exceptions import ClientError
import time

rds_data = boto3.client('rds-data')
rds_client = boto3.client('rds')
s3 = boto3.resource('s3')

def create(properties, physical_id):
  print("Create Event and Properties: {}".format(json.dumps(properties)))

  cluster = properties["DBClusterIdentifier"]
  rds_arn = properties["DBClusterArn"]
  sec_arn = properties["DBSecretArn"]
  database = properties["DBName"]
  bucket = properties['Bucket']
  graphql_api = properties["GraphqlApi"]
  graphql_key = properties["GraphqlKey"]

  print("Begin Modify the Static Resource Config!")
  keep_try = True
  while keep_try:
    try:
      config_object = s3.Object(bucket, 'dist/main.js')
      config_data = config_object.get()['Body'].read().decode('utf-8')
      config_data = config_data.replace("https://xxxxx.appsync-api.ap-northeast-1.amazonaws.com/graphql", graphql_api)
      config_data = config_data.replace("da2-xxxxx", graphql_key)
      config_object.put(Body=config_data)
      keep_try = False
    except ClientError as e:
      if e.response['Error']['Code'] == 'NoSuchKey':
        print('Seelp 5s to wait for the main.js to be uploaded...')
        time.sleep(5)
      else:
        raise

  print('Begin to wait RDS Cluster Alaiable!')

  keep_try = True
  while keep_try:
    try:
      status = rds_client.describe_db_clusters(DBClusterIdentifier=cluster)['DBClusters'][0]['Status']
      if (status=='available'):
        print('Cluster status {}!'.format(status))
        keep_try=False
      else:
        print('Cluster status {}! Sleep 10s...'.format(status))
        time.sleep(10)
    except rds_client.exceptions.DBClusterNotFoundFault:
      print('DB Cluster not found! Sleep 10s...')
      time.sleep(10) 
    
  print('Begin enable RDS HTTP Endpoint!')

  rds_client.modify_db_cluster(DBClusterIdentifier=cluster,EnableHttpEndpoint=True) 
    
  print('Begin Init RDS Schema!')

  with open('initDB.sql') as f:
    init_sqls = f.read().split(';')

  for sql in init_sqls:
    if (len(sql) > 10): 
      rds_data.execute_statement(
        database=database,
        resourceArn=rds_arn,
        secretArn=sec_arn,
        sql=sql
      )

  print('Begin Import Data into RDS!')

  with open('populateDB.sql') as f:
    populate_sqls = f.read().split('\n')

  for sql in populate_sqls:
    if (len(sql) > 10):
      rds_data.execute_statement(
        database=database,
        resourceArn=rds_arn,
        secretArn=sec_arn,
        sql=sql
      )

  print('All the Init Procedure completed!')

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