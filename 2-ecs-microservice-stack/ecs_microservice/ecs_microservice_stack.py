from aws_cdk import (
	aws_ec2 as ec2,
	aws_ecs as ecs,
	aws_rds as rds,
	aws_ecs as ecs,
	aws_ecr_assets as ecr_assets,
	aws_autoscaling as autoscaling,
	aws_elasticloadbalancingv2 as elbv2,
	core
	)
from random import randint


class EcsMicroserviceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        #vpc = ec2.Vpc.from_lookup(self, 'VPC', is_default=True)
        
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2
        )

        
        rdsInst = rds.DatabaseInstance(self, 'SpringPetclinicDB',
          engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.of(mysql_full_version='5.7.40',mysql_major_version='5.7')),
          instance_type=ec2.InstanceType('t2.medium'),
          database_name = 'petclinic',
          credentials=rds.Credentials.from_username(
             username= 'master',
            password=core.SecretValue('Welcome#123456')
          ),
          vpc = vpc,
          deletion_protection = False,
          backup_retention = core.Duration.days(0),
          #removal_policy = RemovalPolicy.DESTROY,
          #vpc_placement = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
          )

        rdsInst.connections.allow_default_port_from_any_ipv4()

        cluster = ecs.Cluster(
            self, 'EcsCluster',
            vpc=vpc
        )

        cluster.add_capacity("DefaultAutoScalingGroup",
                             instance_type=ec2.InstanceType('t2.large'),
                             vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                             min_capacity = 6)

        alb = elbv2.ApplicationLoadBalancer(self, 'EcsLb', vpc=vpc, internet_facing=True)

        listener = alb.add_listener('EcsListener', port=80)

        listener.add_fixed_response('Default-Fix', status_code= '404')
        listener.node.default_child.default_action=[{
          "type": "fixed-response",
          "fixedResponseConfig": {"statusCode": "404"}
        }]

        for s in ['customers', 'vets', 'visits', 'static']:

            asset = ecr_assets.DockerImageAsset(self, 'spring-petclinic-' + s, 
              directory='./work/build/spring-petclinic-' + s + '-service',
              build_args={
                 'JAR_FILE': 'spring-petclinic-' + s + '-service-2.1.4.jar'
              })

            ecs_task = ecs.Ec2TaskDefinition(self, 'TaskDef-' + s)

            env={}

            if s != 'static':
                env = {
                  'SPRING_DATASOURCE_PASSWORD': 'Welcome#123456',
                  'SPRING_DATASOURCE_USERNAME': 'master',
                  'SPRING_PROFILES_ACTIVE': 'mysql',
                  'SPRING_DATASOURCE_URL': 'jdbc:mysql://' + rdsInst.db_instance_endpoint_address + '/petclinic?useUnicode=true&enabledTLSProtocols=TLSv1.2',
                  'SERVER_SERVLET_CONTEXT_PATH': '/api/' + s.rstrip('s')
                }

            ecs_container = ecs_task.add_container(
				'Container-' + s,
				memory_limit_mib=512,
				image=ecs.ContainerImage.from_docker_image_asset(asset),
				logging=ecs.LogDriver.aws_logs(stream_prefix=s),
				environment=env
			)

            ecs_container.add_port_mappings(ecs.PortMapping(container_port=8080))

            ecs_service = ecs.Ec2Service(
	            self, 'Ec2Service-' + s,
	            cluster = cluster,
		        service_name = 'spring-petclinic-' + s,
		        desired_count = 2,
		        task_definition = ecs_task
	        )
            
            if s == 'static':
                parttern = '/*'
                priority = 1100
                check={'path': '/'}
            else:
                parttern = '/api/' + s.rstrip('s') + '/*'
                priority = randint(1, 1000)
                check={'path': '/api/' + s.rstrip('s') + '/manage'}

            target = listener.add_targets(
	        	'ECS-' + s,
	        	path_pattern=parttern,
	        	priority = priority,
	        	port=80, 
	        	targets=[ecs_service],
	        	health_check=check
	        )

        core.CfnOutput(self,"LoadBalancer",export_name="LoadBalancer",value=alb.load_balancer_dns_name)


