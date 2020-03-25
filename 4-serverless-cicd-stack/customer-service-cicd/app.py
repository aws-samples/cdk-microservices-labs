#!/usr/bin/env python3

from aws_cdk import core

from serverless_cicd.serverless_cicd_stack import ServerlessCicdStack
from serverless_lambda.serverless_lambda_stack import ServerlessLambdaStack

app = core.App()
lambda_stack = ServerlessLambdaStack(app, 'customer-lambda-stack')
ServerlessCicdStack(app, "customer-cicd-stack", lambda_code=lambda_stack.lambda_code, custom_resource=lambda_stack.custom_resource)

app.synth()
