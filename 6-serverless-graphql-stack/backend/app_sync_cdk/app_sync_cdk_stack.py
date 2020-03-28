from aws_cdk import core
from aws_cdk.aws_appsync import (
    CfnGraphQLSchema,
    CfnGraphQLApi,
    CfnApiKey,
    CfnDataSource,
    CfnResolver,
    CfnFunctionConfiguration
)
from aws_cdk.aws_iam import (
    Role,
    ServicePrincipal,
    PolicyStatement,
    Effect
)
from aws_cdk.aws_secretsmanager import(
    Secret,
    SecretStringGenerator
)
from aws_cdk.aws_cloudformation import(
    CustomResource,
    CustomResourceProvider
)
from aws_cdk.aws_lambda import(
    SingletonFunction,
    Code,
    Runtime
)
from aws_cdk.aws_s3_deployment import (
    BucketDeployment,
    Source
)

from aws_cdk.aws_rds import CfnDBCluster
from aws_cdk.aws_s3 import Bucket

import os


class AppSyncCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        db_name = 'petclinic'
        db_cluster = 'petclinic-serverless-graphql'

        petclinic_graphql_api = CfnGraphQLApi(
            self, 'PetClinicApi',
            name='PetClinicApi',
            authentication_type='API_KEY'
        )

        petclinic_graphql_key = CfnApiKey(
            self, 'ItemsApiKey',
            api_id=petclinic_graphql_api.attr_api_id
        )

        with open('./definition/petclinic.graphql', 'rt') as f:
            schema_def = f.read()

        petclinic_schema = CfnGraphQLSchema(
            self, 'PetclinicSchema',
            api_id=petclinic_graphql_api.attr_api_id,
            definition=schema_def
        )

        serverless_rds_secret = Secret(
            self, 'PetclinicRDSSecret',
            generate_secret_string=SecretStringGenerator(
                generate_string_key='password',
                secret_string_template='{"username":"master"}',
                exclude_characters= '"@/',
                password_length=16
            )
        )

        serverless_rds_cluster = CfnDBCluster(
            self, 'PetclinicRDSServerless',
            engine='aurora',
            database_name=db_name,
            db_cluster_identifier=db_cluster,
            engine_mode='serverless',
            master_username=serverless_rds_secret.secret_value_from_json('username').to_string(),
            master_user_password=serverless_rds_secret.secret_value_from_json('password').to_string(),
            scaling_configuration=CfnDBCluster.ScalingConfigurationProperty(
              min_capacity=1,
              max_capacity=2,
              auto_pause=False
            )
        )

        serverless_rds_cluster.apply_removal_policy(core.RemovalPolicy.DESTROY)

        serverless_rds_arn='arn:aws:rds:' + self.region + ':' + self.account + ':cluster:' + db_cluster

        website_bucket = Bucket(self, 'PetclinicWebsite',
            website_index_document='index.html',
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        deployment = BucketDeployment(self, 'PetclinicDeployWebsite',
          sources=[Source.asset('../frontend/public')],
          destination_bucket=website_bucket,
          retain_on_delete=False
          #destination_key_prefix='web/static'
        )

        iam_policy = [PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            effect=Effect.ALLOW,
            resources=[serverless_rds_secret.secret_arn]
           ),PolicyStatement(
             actions=["rds-data:ExecuteStatement",
                "rds-data:DeleteItems",
                "rds-data:ExecuteSql",
                "rds-data:GetItems",
                "rds-data:InsertItems",
                "rds-data:UpdateItems"],
             effect=Effect.ALLOW,
             resources=[serverless_rds_arn, serverless_rds_arn + ':*']
          ),PolicyStatement(
              actions=["rds:*"],
              effect=Effect.ALLOW,
              resources=[serverless_rds_arn, serverless_rds_arn + ':*']
          ),PolicyStatement(
                actions=[ "s3:PutObject","s3:PutObjectAcl","s3:PutObjectVersionAcl","s3:GetObject"],
                effect=Effect.ALLOW,
                resources=[website_bucket.bucket_arn + "/*"]
          ),PolicyStatement(
                actions=[ "s3:ListBucket"],
                effect=Effect.ALLOW,
                resources=[website_bucket.bucket_arn]
          )]

        init_resource = CustomResource(self, "PetlinicInitCustomResource",
            provider=CustomResourceProvider.lambda_(
                SingletonFunction(
                    self, "CustomResourceSingleton",
                    uuid="f7d4f730-4ee1-11e8-9c2d-fa7ae01bbebc",
                    code=Code.from_asset('./custom-resource-code'),
                    handler="index.handler",
                    timeout=core.Duration.seconds(600),
                    runtime=Runtime.PYTHON_3_7,
                    initial_policy=iam_policy
                )
            ),
            properties={
                "DBClusterIdentifier": db_cluster,
                "DBClusterArn": serverless_rds_arn,
                "DBSecretArn": serverless_rds_secret.secret_arn,
                "DBName": db_name,
                "Bucket": website_bucket.bucket_name,
                "GraphqlApi": petclinic_graphql_api.attr_graph_ql_url,
                "GraphqlKey": petclinic_graphql_key.attr_api_key
            }
        )

        petclinic_rds_role = Role(
            self, 'PetclinicRDSRole',
            assumed_by=ServicePrincipal('appsync.amazonaws.com')
        )

        petclinic_rds_role.add_to_policy(iam_policy[0])
        petclinic_rds_role.add_to_policy(iam_policy[1])

        data_source = CfnDataSource(
            self, 'PetclinicRDSDatesource',
            api_id=petclinic_graphql_api.attr_api_id,
            type='RELATIONAL_DATABASE',
            name='PetclinicRDSDatesource',
            relational_database_config=CfnDataSource.RelationalDatabaseConfigProperty(
                relational_database_source_type='RDS_HTTP_ENDPOINT',
                rds_http_endpoint_config=CfnDataSource.RdsHttpEndpointConfigProperty(
                    aws_region=self.region,
                    aws_secret_store_arn=serverless_rds_secret.secret_arn,
                    database_name='petclinic',
                    db_cluster_identifier=serverless_rds_arn
                )
            ),
            service_role_arn=petclinic_rds_role.role_arn 
        )
        data_source.add_depends_on(petclinic_schema)
        data_source.add_depends_on(serverless_rds_cluster)

        query_req_path = './definition/template/query/request/'
        query_res_path = './definition/template/query/response/'

        for req_file in os.listdir(query_req_path):
            query_name = req_file.split('.')[0]
            with open(query_req_path + req_file, 'rt') as f:
                query_req = f.read()
            with open(query_res_path + query_name + '.vm', 'rt') as f:
                query_res = f.read()
            pettypes_resolver = CfnResolver(
                self, query_name,
                api_id=petclinic_graphql_api.attr_api_id,
                type_name='Query',
                field_name=query_name,
                data_source_name=data_source.name,
                request_mapping_template=query_req,
                response_mapping_template=query_res
            )
            pettypes_resolver.add_depends_on(data_source)

        func_dict = {}

        func_req_path = './definition/template/function/request/'
        func_res_path = './definition/template/function/response/'

        for req_file in os.listdir(func_req_path):
            func_name = req_file.split('.')[0]
            with open(func_req_path + req_file) as f:
                func_req = f.read()
            with open(func_res_path + func_name + '.vm') as f:
                func_res = f.read()
            func_dict[func_name] = CfnFunctionConfiguration(
                self, func_name,
                api_id=petclinic_graphql_api.attr_api_id,
                data_source_name=data_source.name,
                name=func_name,
                function_version='2018-05-29',
                request_mapping_template=func_req,
                response_mapping_template=func_res
            )
            func_dict[func_name].add_depends_on(data_source)

        query_owner = CfnResolver(
            self, 'QueryOnwer',
            api_id=petclinic_graphql_api.attr_api_id,
            kind='PIPELINE',
            type_name='Query',
            field_name='owner',
            request_mapping_template="{}",
            response_mapping_template="$util.toJson($ctx.result)",
            pipeline_config=CfnResolver.PipelineConfigProperty(
                functions=[func_dict['Query_Owner_getOwnerById'].attr_function_id,
                 func_dict['Query_Owner_getPetsByOwner'].attr_function_id,
                 func_dict['Query_Owner_getVistsByPet'].attr_function_id]
            )
        )

        query_owner.add_depends_on(func_dict['Query_Owner_getOwnerById'])
        query_owner.add_depends_on(func_dict['Query_Owner_getPetsByOwner'])
        query_owner.add_depends_on(func_dict['Query_Owner_getVistsByPet'])

        query_all_owners = CfnResolver(
            self, 'QueryAllOnwers',
            api_id=petclinic_graphql_api.attr_api_id,
            kind='PIPELINE',
            type_name='Query',
            field_name='owners',
            request_mapping_template="{}",
            response_mapping_template="$util.toJson($ctx.result)",
            pipeline_config=CfnResolver.PipelineConfigProperty(
                functions=[func_dict['Query_Owners_getAllOwners'].attr_function_id,
                 func_dict['Query_Owners_getPetsByOwner'].attr_function_id]
            )
        )

        query_all_owners.add_depends_on(func_dict['Query_Owners_getAllOwners'])
        query_all_owners.add_depends_on(func_dict['Query_Owners_getPetsByOwner'])

        query_pet = CfnResolver(
            self, 'QueryPet',
            api_id=petclinic_graphql_api.attr_api_id,
            kind='PIPELINE',
            type_name='Query',
            field_name='pet',
            request_mapping_template="{}",
            response_mapping_template="$util.toJson($ctx.result)",
            pipeline_config=CfnResolver.PipelineConfigProperty(
                functions=[func_dict['Query_Pet_getPetById'].attr_function_id,
                 func_dict['Query_Pet_getVisitByPet'].attr_function_id]
            )
        )

        query_pet.add_depends_on(func_dict['Query_Pet_getPetById'])
        query_pet.add_depends_on(func_dict['Query_Pet_getVisitByPet'])   

        query_vets = CfnResolver(
            self, 'QueryVets',
            api_id=petclinic_graphql_api.attr_api_id,
            kind='PIPELINE',
            type_name='Query',
            field_name='vets',
            request_mapping_template="{}",
            response_mapping_template="$util.toJson($ctx.result)",
            pipeline_config=CfnResolver.PipelineConfigProperty(
                functions=[func_dict['Query_Vets_getVets'].attr_function_id,
                 func_dict['Query_Vets_getSpecByVets'].attr_function_id]
            )
        )

        query_vets.add_depends_on(func_dict['Query_Vets_getVets'])
        query_vets.add_depends_on(func_dict['Query_Vets_getSpecByVets'])

        mutation_req_path = './definition/template/mutation/request/'
        mutation_res_path = './definition/template/mutation/response/'

        for req_file in os.listdir(mutation_req_path):
            mutation_name = req_file.split('.')[0]
            with open(mutation_req_path + req_file) as f:
                func_req = f.read()
            with open(mutation_res_path + mutation_name + '.vm') as f:
                func_res = f.read()
            mutation = CfnResolver(
                self, mutation_name,
                api_id=petclinic_graphql_api.attr_api_id,
                type_name='Mutation',
                field_name=mutation_name,
                data_source_name=data_source.name,
                request_mapping_template=func_req,
                response_mapping_template=func_res
            )
            mutation.add_depends_on(data_source)

        core.CfnOutput(self,"GraphqlPetclinicWebsiteUrl",export_name="GraphqlPetclinicWebsiteUrl",value=website_bucket.bucket_website_url)