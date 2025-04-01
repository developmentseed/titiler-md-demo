# Demo of titiler.xarray

---

**Source Code**: <a href="https://github.com/developmentseed/titiler-md-demo" target="_blank">https://github.com/developmentseed/titiler-md-demo</a>

---

## Running Locally

```bash
git clone https://github.com/developmentseed/titiler-md-demo.git

# It's recommended to install dependencies in a virtual environment
python -m venv .venv
source .venv/bin/activate

python -m pip install -e runtimes/ uvicorn
uvicorn runtimes.titiler_md_demo.main:app --reload
```

## Deployments

The following steps detail how to to setup and deploy the CDK stack from your local machine.

1. Install CDK and connect to your AWS account. This step is only necessary once per AWS account.

```bash
# Download titiler repo
git clone https://github.com/developmentseed/titiler-md-demo.git

# Create a virtual environment
python -m pip install --upgrade virtualenv
virtualenv infrastructure/aws/.venv
source infrastructure/aws/.venv/bin/activate

# install cdk dependencies
python -m pip install -r infrastructure/aws/requirements-cdk.txt

# Install node dependency
npm --prefix infrastructure/aws install

# Deploys the CDK toolkit stack into an AWS environment
npm --prefix infrastructure/aws run cdk -- bootstrap

# or to a specific region and or using AWS profile
AWS_DEFAULT_REGION=us-west-2 AWS_REGION=us-west-2 AWS_PROFILE=myprofile npm --prefix infrastructure/aws run cdk -- bootstrap
```

2. Update settings

Set environment variable or hard code in `infrastructure/aws/.env` file (e.g `STACK_STAGE=testing`).

3. Pre-Generate CFN template

```bash
npm --prefix infrastructure/aws run cdk -- synth  # Synthesizes and prints the CloudFormation template for this stack
```

4. Deploy

```bash
STACK_STAGE=staging npm --prefix infrastructure/aws run cdk -- deploy titiler-multidim-staging

# Deploy in specific region
AWS_DEFAULT_REGION=us-west-2 AWS_REGION=us-west-2 AWS_PROFILE=prof npm --prefix infrastructure/aws run cdk -- deploy titiler-multidim-production
```
