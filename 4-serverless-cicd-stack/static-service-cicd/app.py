#!/usr/bin/env python3

from aws_cdk import core

from static_cicd.static_cicd_stack import StaticCicdStack

app = core.App()
StaticCicdStack(app, "static-cicd-stack")

app.synth()
