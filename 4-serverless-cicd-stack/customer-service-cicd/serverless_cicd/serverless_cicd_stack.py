from aws_cdk import (
	aws_codepipeline as _pipeline,
	aws_codebuild as _build,
	aws_codecommit as _commit,
	aws_codepipeline_actions as _action,
	aws_lambda as _lambda,
	core
	)


class ServerlessCicdStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, lambda_code: _lambda.CfnParametersCode, custom_resource: _lambda.CfnParametersCode, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        self.lambda_code = lambda_code
        self.custom_resource = custom_resource

        code = _commit.Repository(self, 'CustomerServerlessCode',
        	   repository_name='spring-petclinic-customers-serverless'
        	)

        lambda_project = _build.PipelineProject(self, 'CustomerLambdaBuild',
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
	            'commands': 'mvn package',
	          },
            'post_build': {
               'commands': [
                  'mkdir deploy',
                  'cp target/spring-petclinic-customers-serverless-2.0.7.RELEASE.jar deploy/',
                  'cd deploy && jar xvf spring-petclinic-customers-serverless-2.0.7.RELEASE.jar',
                  'rm spring-petclinic-customers-serverless-2.0.7.RELEASE.jar',
               ]
            }
	        },
	        'artifacts': {
	          'base-directory': 'deploy',
	          'files': ['**/*']
	        },
	      }),
	      environment=_build.BuildEnvironment(
	      	build_image=_build.LinuxBuildImage.STANDARD_2_0)
	    )

        cdk_project = _build.PipelineProject(self, 'CustomerCdkBuild',
	    	build_spec=_build.BuildSpec.from_object({
               'version': 0.2,
               'phases': {
                  'install': {
                     'runtime-versions':{
                        'python': '3.7',
                        'nodejs': '10'
                     },
                    'commands':[
                      'npm install -g aws-cdk',
                      'pip install -r requirements.txt'
                    ]
                  },
                  'build':{
                     'commands': [
                     'cdk synth -o dist',
                     ]
                  }
               },
               'artifacts': {
                   'secondary-artifacts': {
                      'CdkBuildOutput': {
                        'base-directory': 'dist',
                        'files': ['customer-lambda-stack.template.json']
                      },
                      'CustomRecoureOutput': {
                        'base-directory': 'custom-resource-code',
                        'discard-paths': 'yes',
                        'files': ['index.py', 'owner.json', 'cfnresponse.py']
                      }
                   }
                }
	    	}),
            environment=_build.BuildEnvironment(
            	build_image=_build.LinuxBuildImage.STANDARD_2_0
            )
	    )

        source_output = _pipeline.Artifact('SourceOutput')
        cdk_build_output = _pipeline.Artifact('CdkBuildOutput')
        lambda_build_output = _pipeline.Artifact('LambdaBuildOutput')
        custom_resource_output = _pipeline.Artifact('CustomRecoureOutput')

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
                        	  action_name='CodeBuild_CDK',
                        	  project=cdk_project,
                        	  input=source_output,
                            outputs=[cdk_build_output, custom_resource_output]
                        	),_action.CodeBuildAction(
                        	  action_name='CodeBuild_Lambda',
                        	  project=lambda_project,
                        	  input=source_output,
                            outputs=[lambda_build_output]
                        )]
                    },{
                        'stageName': 'Deploy',
                        'actions': [_action.CloudFormationCreateUpdateStackAction(
                            action_name='Lambda_CFN_Deploy',
                            template_path=cdk_build_output.at_path('customer-lambda-stack.template.json'),
                            stack_name='customer-lambda-stack',
                            admin_permissions=True,
                            parameter_overrides={**self.lambda_code.assign(
                            	bucket_name=lambda_build_output.bucket_name, 
                            	object_key=lambda_build_output.object_key),
                            **self.custom_resource.assign(
                              bucket_name=custom_resource_output.bucket_name,
                              object_key=custom_resource_output.object_key)},
                            extra_inputs=[lambda_build_output, custom_resource_output]
                         )]
                    }]
            )