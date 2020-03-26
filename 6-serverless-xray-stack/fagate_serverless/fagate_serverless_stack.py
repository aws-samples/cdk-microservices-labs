from random import randint
from aws_cdk import core
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_elasticloadbalancingv2 import(
    ApplicationLoadBalancer,
    HealthCheck
)
from aws_cdk.aws_ecr_assets import DockerImageAsset

from aws_cdk.aws_ecs import(
    ContainerImage,
    Cluster,
    FargateTaskDefinition,
    LogDriver,
    PortMapping,
    FargateService,
    Protocol
)

from aws_cdk.aws_s3_deployment import(
    BucketDeployment,
    Source
)

from aws_cdk.aws_iam import(
    PolicyStatement,
    Effect
)

from aws_cdk.aws_dynamodb import(
    Table,
    AttributeType
)

from aws_cdk.aws_lambda import(
    SingletonFunction,
    InlineCode,
    Runtime
)

from aws_cdk.aws_cloudformation import(
    CustomResourceProvider,
    CustomResource
)



class FagateServerlessStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        vpc = Vpc(
            self, "MyVpc",
            max_azs=2
        )

        ecs_cluster = Cluster(
            self, 'FagateCluster',
            vpc=vpc
        )

        alb = ApplicationLoadBalancer(self, 'EcsLb', vpc=vpc, internet_facing=True)

        listener = alb.add_listener('EcsListener', port=80)

        listener.add_fixed_response('Default-Fix', status_code= '404')
        listener.node.default_child.default_action=[{
          "type": "fixed-response",
          "fixedResponseConfig": {"statusCode": "404"}
        }]
        
        website_bucket = Bucket(self, 'PetclinicWebsite',
            website_index_document='index.html',
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )
        
        deployment = BucketDeployment(self, 'PetclinicDeployWebsite',
          sources=[Source.asset('./spring-petclinic-static')],
          destination_bucket=website_bucket,
          retain_on_delete=False
          #destination_key_prefix='web/static'
        )
        
        # Modify the config.js with CF custome resource
        modify_policy = [PolicyStatement(
                actions=[ "s3:PutObject","s3:PutObjectAcl","s3:PutObjectVersionAcl","s3:GetObject"],
                effect=Effect.ALLOW,
                resources=[website_bucket.bucket_arn + "/*"]
            ),PolicyStatement(
                actions=[ "s3:ListBucket"],
                effect=Effect.ALLOW,
                resources=[website_bucket.bucket_arn]
            ),PolicyStatement(
                actions=[ "dynamodb:*"],
                effect=Effect.ALLOW,
                resources=["arn:aws:dynamodb:" + self.region + ":" + self.account + ":*"]
            )]
            
        with open("custom-resource-code/init.py", encoding="utf-8") as fp:
            code_body = fp.read()
        
        dynamodb_tables = []
        
        
        for s in ['customers', 'vets', 'visits']:
            table = Table(self, s.capitalize() + 'Table',
              partition_key={ 'name': 'id', 'type': AttributeType.STRING },
              removal_policy=core.RemovalPolicy.DESTROY,
              read_capacity=5,
              write_capacity=5,
            )
            
            dynamodb_tables.append(table.table_name)

            asset = DockerImageAsset(self, 'spring-petclinic-' + s,
              repository_name = self.stack_name + '-' + s,
              directory='./spring-petclinic-serverless/spring-petclinic-' + s + '-serverless',
              build_args={
                 'JAR_FILE': 'spring-petclinic-' + s + '-serverless-2.0.7.jar'
              })

            ecs_task = FargateTaskDefinition(
                self, 'TaskDef-Fargate-' + s,
                memory_limit_mib=512,
                cpu=256
            )

            ecs_task.add_to_task_role_policy(PolicyStatement(
                   actions=[ "dynamodb:*"],
                   effect=Effect.ALLOW,
                   resources=[table.table_arn]
            ))

            ecs_task.add_to_task_role_policy(PolicyStatement(
                   actions=['xray:*'],
                   effect=Effect.ALLOW,
                   resources=['*']
            ))

            env = {
              'DYNAMODB_TABLE_NAME': table.table_name,
              'SERVER_SERVLET_CONTEXT_PATH': '/api/' + s.rstrip('s')
            }

            ecs_container = ecs_task.add_container(
                'Container-' + s,
                image=ContainerImage.from_docker_image_asset(asset),
                logging=LogDriver.aws_logs(stream_prefix=s),
                environment=env
            )

            ecs_container.add_port_mappings(PortMapping(container_port=8080))

            # Sidecare Container for X-Ray
            ecs_sidecar_container = ecs_task.add_container(
                'Sidecar-Xray-' + s,
                image=ContainerImage.from_registry('amazon/aws-xray-daemon')
            )

            ecs_sidecar_container.add_port_mappings(PortMapping(container_port=2000, protocol=Protocol.UDP))

            ecs_service = FargateService(
                self, 'FargateService-' + s,
                cluster = ecs_cluster,
                service_name = 'spring-petclinic-' + s,
                desired_count = 2,
                task_definition = ecs_task
            )

            parttern = '/api/' + s.rstrip('s') + '/*'
            priority = randint(1, 10)*len(s)
            check=HealthCheck(
                path='/api/' + s.rstrip('s') + '/manage',
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
            )


            target = listener.add_targets(
                'ECS-' + s,
                path_pattern=parttern,
                priority = priority,
                port=80,
                targets=[ecs_service],
                health_check=check
            )
            
            
        resource = CustomResource(self, "S3ModifyCustomResource",
            provider=CustomResourceProvider.lambda_(
                SingletonFunction(
                    self, "CustomResourceSingleton",
                    uuid="f7d4f730-4ee1-11e8-9c2d-fa7ae01bbebc",
                    code=InlineCode(code_body),
                    handler="index.handler",
                    timeout=core.Duration.seconds(300),
                    runtime=Runtime.PYTHON_3_7,
                    initial_policy=modify_policy
                )
            ),
            properties={"Bucket": website_bucket.bucket_name, 
                        "InvokeUrl":'http://' + alb.load_balancer_dns_name +'/',
                        "DynamoDBTables": dynamodb_tables
            }
        )
        
        core.CfnOutput(self,"FagateALBUrl",export_name="FagateALBUrl",value=alb.load_balancer_dns_name)
        core.CfnOutput(self,"FagatePetclinicWebsiteUrl",export_name="FagatePetclinicWebsiteUrl",value=website_bucket.bucket_website_url)

