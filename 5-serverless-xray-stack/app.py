#!/usr/bin/env python3

from aws_cdk import core

from fagate_serverless.fagate_serverless_stack import FagateServerlessStack


app = core.App()
FagateServerlessStack(app, "serverless-xray-stack")

app.synth()
