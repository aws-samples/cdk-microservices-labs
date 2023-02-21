## Introduction

## Hugo Style Workshop Documents

If you want more detail workshop describion documents pelase visit [this site](http://cloudnative-immersion-day.s3-website-ap-northeast-1.amazonaws.com/)

### Microservices Deployed Using Cloud Development Kit

This repository contains the Lab of Microservices Deployed on ECS using [AWS Cloud Development Kit](https://github.com/awslabs/aws-cdk).


We will take the [Spring Pet Clinic](https://github.com/spring-projects/spring-petclinic) as the base to extend from. And we will break down the Monolith Architecture to Microservice base on [Distributed version of the Spring PetClinic Sample](https://github.com/spring-petclinic/spring-petclinic-microservices).

So lets get to it,

1. [Part One: Moving existing Java Spring application to a container deployed using ECS](1-ecs-monolith-stack)

2. [Part Two: Breaking the monolith apart into microservices on ECS](2-ecs-microservice-stack)

3. [Part Three: Migrate to Serverless and API Gateway Parten](3-serverless-microservice-stack)

4. [Part Four: Build CI/CD Pipeline for Serverless Projects](4-serverless-cicd-stack)

5. [Part Five: Microservice Tracing & Monitoring](5-serverless-xray-stack)

6. [Part Six: GraphQL for data driven application development](6-serverless-graphql-stack)


## Prerequisites

You can run this Lab in any Linux or Mac OS system. You will need to have the latest version of the AWS CLI, maven and AWS CDK installed before running the deployment script.  If you need help installing either of these components, please follow the links below:

1. [Installing the AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
2. [Installing Maven](https://maven.apache.org/install.html)
3. [Installing Docker](https://docs.docker.com/engine/installation/)
4. [Installing Python](https://www.python.org/downloads/)
5. [Installing JQ](https://stedolan.github.io/jq/download/)
6. [Installing CDK Python Version](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#python)

### Setup Lab Environment on AWS Cloud9

You can reference [this Guide](https://docs.aws.amazon.com/cloud9/latest/user-guide/sample-cdk.html) to setup your Cloud9 quickly setup your development environment. To complete this Lab you need some other steps:

1. Confirm the CDK version:
```bash
cdk --version
```
If CDK is not installed use the following command to install it:
```bash
npm install -g aws-cdk
```
2. Confirm the Java version:
```bash
java -version
```
3. Confirm the Python version:
```bash
python --version
```
4. Confirm that git is installed:
```bash
python --version
```
5. Confirm that git-commit-remote is installed. The below command should return a path to git-remote-codecommit:
```bash
which git-remote-codecommit
```
If git-remote-codecommit is not instalalled use the following command to install it:
```bash
pip install git-remote-codecommit
```
6. Connect to Cloud9 terminal and Git clone this project, please note we must use `--recurse-submodules` flag to download all other third parties codes:
```bash
git clone --recurse-submodules https://github.com/aws-samples/cdk-microservices-labs.git
```