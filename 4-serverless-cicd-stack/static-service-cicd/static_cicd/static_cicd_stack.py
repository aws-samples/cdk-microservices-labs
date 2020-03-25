from aws_cdk import (
	aws_codepipeline as _pipeline,
	aws_codebuild as _build,
	aws_codecommit as _commit,
	aws_codepipeline_actions as _action,
    aws_apigateway as _apigw,
    aws_s3_deployment as _s3deploy,
    aws_events as _events,
	aws_lambda as _lambda,
    aws_s3 as _s3,
	core
	)


class StaticCicdStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
            
        base_api = _apigw.RestApi(self, 'PetclinicApiGatewayWithCors')
            
        api_resource = base_api.root.add_resource('api')

        self.add_cors_options(api_resource)
        
        website_bucket = _s3.Bucket(self, 'PetclinicWebsite',
            website_index_document='index.html',
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )
        
        # Warm Lambda function Event rule
        event_rule = _events.Rule(self, 'PetclinicLambdaWarmRule',
            schedule=_events.Schedule.rate(core.Duration.minutes(3))
        )

        code = _commit.Repository(self, 'ServerlessCode',
        	   repository_name='spring-petclinic-static-resource'
        	)

        build_project = _build.PipelineProject(self, 'StaticWebBuild',
          build_spec=_build.BuildSpec.from_object({
            'version': 0.2,
            'phases': {
               'install': {
                 'runtime-versions': {
                   'java': 'openjdk8'
                 },
                 'commands': []
              },
               'build': {
                 'commands': [
                    'mv scripts/config.js scripts/config.js.origin',
                    'sed -e "s,http://localhost:8081/,$API_ENDPOINT,g" scripts/config.js.origin > scripts/config.js'
                ]
              },
            },
            'artifacts': {
              'files': '**/*'
            },
          }),
          environment_variables={'API_ENDPOINT': _build.BuildEnvironmentVariable(value=base_api.url)},
          environment=_build.BuildEnvironment(
            build_image=_build.LinuxBuildImage.STANDARD_2_0)
        )

        source_output = _pipeline.Artifact('SourceOutput')
        build_output = _pipeline.Artifact('BuildOutput')

        pipline = _pipeline.Pipeline(self, 'ServerlessPipeline',
                stages=[
                    {
                        'stageName': 'Source',
                        'actions': [_action.CodeCommitSourceAction(
                        	action_name='CodeCommit_Source',
                        	repository=code,
                        	output=source_output
                        	)]
                    },{
                        'stageName': 'Build',
                        'actions':[_action.CodeBuildAction(
                            action_name='CodeBuild_Static',
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                            )]
                    },{
                        'stageName': 'Deploy',
                        'actions': [_action.S3DeployAction(
                            action_name='Web_Static_Deploy',
                            input=build_output,
                            bucket=website_bucket
                         )]
                    }]
            )
        core.CfnOutput(self, 'RuleArn', export_name='RuleArn', value=event_rule.rule_arn)
        core.CfnOutput(self, 'PetclinicApiGatewayWithCorsId', export_name='PetclinicApiGatewayWithCorsId', value=base_api.rest_api_id)
        core.CfnOutput(self, "PetclinicWebsiteUrl",export_name="PetclinicWebsiteUrl",value=website_bucket.bucket_website_url)


    def add_cors_options(self, apigw_resource):
        apigw_resource.add_method('OPTIONS', _apigw.MockIntegration(
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': "'cache-control,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Methods': "'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT'"
                }
            }
            ],
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