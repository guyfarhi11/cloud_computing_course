#!/bin/bash

# Variables
GITHUB_REPO_URL="https://github.com/guyfarhi11/cloud_computing_course.git"
PROJECT_DIR="pulumi_run"
MAIN_PY_PATH="__main__.py"

# Clone the Pulumi project from GitHub
git clone $GITHUB_REPO_URL temp-repo

# Create the project directory
mkdir $PROJECT_DIR

# Navigate to the project directory
cd $PROJECT_DIR

# Run Pulumi new aws-python
pulumi new aws-python -y

# Replace the generated __main__.py with the one from the GitHub repository
cp ../temp-repo/$MAIN_PY_PATH ./$MAIN_PY_PATH


# Initialize Pulumi stack
pulumi stack init dev

# Set the AWS region (you can change this to your preferred region)
pulumi config set aws:region us-east-1

# Deploy the Pulumi stack
pulumi up -y

# Cleanup: remove the temporary cloned repository
cd ..
rm -rf temp-repo

echo "Pulumi stack deployed successfully."
