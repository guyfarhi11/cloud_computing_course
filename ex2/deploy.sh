#!/bin/bash

# Variables
GITHUB_REPO_URL="https://github.com/guyfarhi11/cloud_computing_course.git"
PROJECT_DIR="whatsup_app"
MAIN_PY_PATH_FROM_REPO="pulumi_deploy/__main__.py"

git clone $GITHUB_REPO_URL temp-repo
mkdir $PROJECT_DIR
cd $PROJECT_DIR

# Run Pulumi new aws-python
pulumi new aws-python -y

# Replace the generated __main__.py with the one from the GitHub repository
cp ../temp-repo/$MAIN_PY_PATH ./$MAIN_PY_PATH


# Initialize Pulumi stack
pulumi stack init dev

# Set the AWS region
pulumi config set aws:region us-east-1

# Deploy the Pulumi stack
pulumi up -y

# Cleanup:
cd ..
rm -rf temp-repo

echo "Pulumi stack deployed successfully."
