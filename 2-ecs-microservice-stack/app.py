#!/usr/bin/env python3

from aws_cdk import core

from ecs_microservice.ecs_microservice_stack import EcsMicroserviceStack


app = core.App()
EcsMicroserviceStack(app, "ecs-microservice-stack")

app.synth()
