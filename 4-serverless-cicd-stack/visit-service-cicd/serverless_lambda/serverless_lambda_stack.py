from aws_cdk import (
	aws_dynamodb as _dynamodb,
	aws_apigateway as _apigw,
	aws_lambda as _lambda,
	aws_iam as iam,
    aws_codedeploy as _deploy,
    aws_cloudformation as _cfn,
	core
)
import time

class ServerlessLambdaStack(core.Stack):

    lambda_code = _lambda.Code.from_cfn_parameters()
    custom_resource = _lambda.Code.from_cfn_parameters()

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


        table = _dynamodb.Table(self, 'VisitTable',
            partition_key={ 'name': 'id', 'type': _dynamodb.AttributeType.STRING },
            removal_policy=core.RemovalPolicy.DESTROY,
            read_capacity=5,
            write_capacity=5,
        )

        # Modify the config.js with CF custome resource

        modify_policy = [iam.PolicyStatement(
                actions=[ "dynamodb:*"],
                effect=iam.Effect.ALLOW,
                resources=["arn:aws:dynamodb:" + core.Aws.REGION + ":" + core.Aws.ACCOUNT_ID + ":*"]
            )]

        resource = _cfn.CustomResource(self, "VisitDataImportCustomResource",
            provider=_cfn.CustomResourceProvider.lambda_(
                _lambda.SingletonFunction(
                    self, "CustomResourceSingleton",
                    uuid="f7d4f730-4ee1-11e8-9c2d-fa7ae01bbebc",
                    code=self.custom_resource,
                    handler="index.handler",
                    timeout=core.Duration.seconds(300),
                    runtime=_lambda.Runtime.PYTHON_3_7,
                    initial_policy=modify_policy
                )
            ),
            properties={"DynamoDBTable": table.table_name}
        )

        base_lambda = _lambda.Function(self,'ApiPetclinicVisitLambda',
            handler='org.springframework.samples.petclinic.visits.StreamLambdaHandler::handleRequest',
            runtime=_lambda.Runtime.JAVA_8,
            code=self.lambda_code,
            memory_size=1024,
            timeout=core.Duration.seconds(300),
            initial_policy=lambda_policies,
            environment={"DYNAMODB_TABLE_NAME":table.table_name, "SERVER_SERVLET_CONTEXT_PATH":"/api/visit"}
        )
       

        version = base_lambda.add_version(str(round(time.time())))

        alias = _lambda.Alias(self, 'ApiPetclinicVisitLambdaAlias',
          alias_name='Prod',
          version=version
        )

        _deploy.LambdaDeploymentGroup(self, 'ApiPetclinicVisitDeploymentGroup',
          alias=alias,
          deployment_config=_deploy.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE
        )
