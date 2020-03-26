
# Welcome to Spring Petclinic Serverless CDK Python project!

This is a project for Python development with CDK. And you must have meet [requirement](../README.md#prerequisites) before to start below.

First of all we need create the Spring Boot deployment JAR using:

```bash
cd spring-petclinic-serverless && ./mvnw package
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

After review the CloudFormation template you can upload all the Lambda Function JARs, static files and deploy all the Infracture codes using:

```bash
cdk deploy
```

Check the Spring Petclinic Application deployment is success by browse the CDK output AWS ELB url like:

```bash
serverless-stack.PetclinicApiGatewayWithCorsEndpoint122A21C4 = https://gw5lflv1q3.execute-api.ap-northeast-1.amazonaws.com/prod/
serverless-stack.PetclinicWebsiteUrl = http://serverless-stack-petclinicwebsitebcda6fa7-yo4jhabxfujm.s3-website-ap-northeast-1.amazonaws.com
```

Finally you can clean up the whole stack by using:

```bash
cdk destory
```