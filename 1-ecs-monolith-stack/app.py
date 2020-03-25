#!/usr/bin/env python3

from aws_cdk import core

from ecs_monolith.ecs_monolith_stack import EcsMonolithStack

app = core.App()

EcsMonolithStack(app, "ecs-monolith-stack")

app.synth()
