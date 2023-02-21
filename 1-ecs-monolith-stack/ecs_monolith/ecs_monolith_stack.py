from aws_cdk import (
	aws_ec2 as ec2,
	aws_ecs as ecs,
	aws_rds as rds,
	aws_ecs as ecs,
  aws_ecr_assets as ecr_assets,
	aws_autoscaling as autoscaling,
	aws_ecs_patterns as ecs_patterns,
	core
	)


class EcsMonolithStack(core.Stack):

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

        asset = ecr_assets.DockerImageAsset(self, 'spring-petclinic', 
          directory='./docker/',
          build_args={
             'JAR_FILE': 'spring-petclinic-2.1.0.BUILD-SNAPSHOT.jar'
          })

        cluster.add_capacity("DefaultAutoScalingGroup",
                             instance_type=ec2.InstanceType('t2.large'),
                             vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                             min_capacity = 2)

        ecs_service = ecs_patterns.ApplicationLoadBalancedEc2Service(
            self, "Ec2Service",
            cluster=cluster,
            memory_limit_mib=1024,
            service_name='spring-petclinic',
            desired_count= 2,
            task_image_options = {
              "image": ecs.ContainerImage.from_docker_image_asset(asset),
              "container_name": 'spring-petclinic',
              "container_port": 8080,
              "environment":  {
                'SPRING_DATASOURCE_PASSWORD': 'Welcome#123456',
                'SPRING_DATASOURCE_USERNAME': 'master',
                'SPRING_PROFILES_ACTIVE': 'mysql',
                'SPRING_DATASOURCE_URL': 'jdbc:mysql://' + rdsInst.db_instance_endpoint_address + '/petclinic?useUnicode=true&enabledTLSProtocols=TLSv1.2'
              }
            }
        )
