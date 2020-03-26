
# Welcome to Spring Petclinic GgraphQL Serverless CDK Python project!

This is a project for Python development with CDK. And you must have meet [requirement](../README.md#prerequisites) before to start below.

First of all we will install `Yarn` to generate our frontend static resource, you can reference [this guide](https://yarnpkg.com/en/docs/install#centos-stable) to have more detail informaiton.

```bash
curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | sudo tee /etc/yum.repos.d/yarn.repo
sudo yum install yarn
```
Copy some modified the source frontend codes:
```bash
mkdir frontend \
  && cp -r ./spring-petclinic-graphql/frontend/* frontend/ \
  && cp createGraphQLClient.tsx ./frontend/src/ \
  && cp Footer.tsx ./frontend/src/app/ui/Layout/ \
  && cp AWS-AppSync.svg ./frontend/public/images/ \
  && cp webpack.config.js ./frontend/ \
  && cp AddPetPage.tsx ./frontend/src/app/domain/pet/AddPetPage \
  && cp UpdatePetPage.tsx ./frontend/src/app/domain/pet/UpdatePetPage \
  && cp DateInput.tsx ./frontend/src/app/components/form/FormElements/elements
```

Next we need create the Spring Petclinic Frontend static resource:

```bash
cd frontend && yarn install && yarn dist
```

We also manually create a virtualenv on MacOS and Linux in this project root folder:

```bash
cd ../backend && python3 -m venv .env
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

After review the CloudFormation template you can upload all the Lambda Function source codes, static files and deploy all the Infracture codes including GgraphQL definitions using:

```bash
cdk deploy
```

When the command run completed you can open the new deploy Web static page to login in the GrapshQL version Pet Clinic Application.

Finally you can clean up the whole stack by using:

```bash
cdk destroy
```