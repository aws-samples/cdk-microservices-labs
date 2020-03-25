
# Welcome to Spring Petclinic Monolith CDK Python project!

This is a project for Python development with CDK. And you must have meet [requirement](../README.md#prerequisites) before to start below.

First of all we need create the Spring Boot deployment JAR using:

```bash
cd spring-petclinic && ./mvnw package -Dmaven.test.skip=true && mv target ../docker/
```

We also manually create a virtualenv on MacOS and Linux in this project root folder:

```bash
cd ../ && python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```bash
source .env/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```bash
pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```bash
cdk synth
```

After review the CloudFormation template you can create the Docker Image which will upload to ECR Repo and deploy all the Infracture codes using:

```bash
cdk deploy
```

Check the Spring Petclinic Application deployment is success by browse the CDK output AWS ELB url like

```
ecs-monolith-stack.Ec2ServiceServiceURL8FE8FAED = http://ecs-m-Ec2Se-17QZ5ETAVT9IO-2074181029.ap-northeast-1.elb.amazonaws.com
```

Finally you can clean up the whole stack by using:

```bash
cdk destory
```