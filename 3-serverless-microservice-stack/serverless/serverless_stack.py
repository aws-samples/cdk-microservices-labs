from aws_cdk import (
	aws_s3 as _s3,
	aws_dynamodb as _dynamodb,
	aws_apigateway as _apigw,
	aws_lambda as _lambda,
	aws_s3_deployment as _s3deploy,
	aws_iam as iam,
	aws_cloudformation as _cfn,
	aws_events as _event,
	aws_events_targets as _target,
	core
	)

class ServerlessStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        
        lambda_policies = [iam.PolicyStatement(
                actions=[ "logs:CreateLogStream", "logs:PutLogEvents", "logs:CreateLogGroup"],
                effect=iam.Effect.ALLOW,
                resources=["arn:aws:logs:" + core.Aws.REGION + ":" + core.Aws.ACCOUNT_ID + ":*"]
            ), iam.PolicyStatement(
                actions=[ "dynamodb:*"],
                effect=iam.Effect.ALLOW,
                resources=["arn:aws:dynamodb:" + core.Aws.REGION + ":" + core.Aws.ACCOUNT_ID + ":*"]
            )]
            
        base_api = _apigw.RestApi(self, 'PetclinicApiGatewayWithCors',
            rest_api_name='PetclinicApiGatewayWithCors')
            
        api_resource = base_api.root.add_resource('api')
        
        website_bucket = _s3.Bucket(self, 'PetclinicWebsite',
            website_index_document='index.html',
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )
        
        deployment = _s3deploy.BucketDeployment(self, 'PetclinicDeployWebsite',
          sources=[_s3deploy.Source.asset('./spring-petclinic-static')],
          destination_bucket=website_bucket,
          retain_on_delete=False
          #destination_key_prefix='web/static'
        )
        
        # Modify the config.js with CF custome resource
        modify_policy = [iam.PolicyStatement(
                actions=[ "s3:PutObject","s3:PutObjectAcl","s3:PutObjectVersionAcl","s3:GetObject"],
                effect=iam.Effect.ALLOW,
                resources=[website_bucket.bucket_arn + "/*"]
            ),iam.PolicyStatement(
                actions=[ "s3:ListBucket"],
                effect=iam.Effect.ALLOW,
                resources=[website_bucket.bucket_arn]
            ),iam.PolicyStatement(
                actions=[ "dynamodb:*"],
                effect=iam.Effect.ALLOW,
                resources=["arn:aws:dynamodb:" + core.Aws.REGION + ":" + core.Aws.ACCOUNT_ID + ":*"]
            )]
            
        with open("custom-resource-code/init.py", encoding="utf-8") as fp:
            code_body = fp.read()
        
        dynamodb_tables = []
        
        for service in ['customer', 'vet', 'visit']:
            table = _dynamodb.Table(self, service.capitalize() + 'Table',
              partition_key={ 'name': 'id', 'type': _dynamodb.AttributeType.STRING },
              removal_policy=core.RemovalPolicy.DESTROY,
              read_capacity=5,
              write_capacity=5,
            )
            
            dynamodb_tables.append(table.table_name)
                
            base_lambda = _lambda.Function(self,'ApiPetclinic' + service.capitalize() + 'Lambda',
                handler='org.springframework.samples.petclinic.' + service + 's.StreamLambdaHandler::handleRequest',
                runtime=_lambda.Runtime.JAVA_8,
                code=_lambda.Code.asset('./spring-petclinic-serverless/spring-petclinic-' + service +'s-serverless/target/spring-petclinic-' + service +'s-serverless-2.0.7.jar'),
                memory_size=1024,
                timeout=core.Duration.seconds(300),
                initial_policy=lambda_policies,
                environment={"DYNAMODB_TABLE_NAME":table.table_name, "SERVER_SERVLET_CONTEXT_PATH":"/api/" + service},
                current_version_options=_lambda.VersionOptions(provisioned_concurrent_executions=5) #Added for warm the Java Lambda
            )
        
            entity = api_resource.add_resource(service)
            entity.add_proxy(default_integration=_apigw.LambdaIntegration(base_lambda))
            self.add_cors_options(entity)
            
        resource = _cfn.CustomResource(self, "S3ModifyCustomResource",
            provider=_cfn.CustomResourceProvider.lambda_(
                _lambda.SingletonFunction(
                    self, "CustomResourceSingleton",
                    uuid="f7d4f730-4ee1-11e8-9c2d-fa7ae01bbebc",
                    code=_lambda.InlineCode(code_body),
                    handler="index.handler",
                    timeout=core.Duration.seconds(300),
                    runtime=_lambda.Runtime.PYTHON_3_7,
                    initial_policy=modify_policy
                )
            ),
            properties={"Bucket": website_bucket.bucket_name, 
                        "InvokeUrl":base_api.url,
                        "DynamoDBTables": dynamodb_tables
            }
        )
        
        core.CfnOutput(self,"PetclinicWebsiteUrl",export_name="PetclinicWebsiteUrl",value=website_bucket.bucket_website_url)


    def add_cors_options(self, apigw_resource):
        apigw_resource.add_method('OPTIONS', _apigw.MockIntegration(
                integration_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Headers': "'cache-control,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Methods': "'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT'"
                    }
                }],
                passthrough_behavior=_apigw.PassthroughBehavior.WHEN_NO_MATCH,
                request_templates={"application/json":"{\"statusCode\":200}"}
           ),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Origin': True,
                    }
                }
            ],
        )
