import pulumi
import pulumi_aws as aws

# Create a new security group
group = aws.ec2.SecurityGroup('web-secgrp',
    description='Enable HTTP access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0'] },  # SSH access
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] }   # HTTP access
    ])

# Create a new EC2 instance
server = aws.ec2.Instance('web-server',
    instance_type='t3.micro',
    ami='ami-08a0d1e16fc3f61ea',  # This is the Amazon Linux 2 AMI in us-east-1
    security_groups=[group.name],
    user_data="""
    # Update package manager and install necessary packages
    sudo yum update
    sudo yum -y install python-pip python3 python3-pip git sqlite
    
    # Create project directory and set up environment
    mkdir whatsup_app
    cd whatsup_app
    
    # Clone the repository and set up virtual environment
    git clone https://github.com/guyfarhi11/cloud_computing_course.git
    cd cloud_computing_course/ex2
    python3 -m venv venv
    source venv/bin/activate

    pip install flask
    
    python3 app.py


""",
)

# Export the public IP of the created instance
pulumi.export('publicIp', server.public_ip)
pulumi.export('publicDns', server.public_dns)
