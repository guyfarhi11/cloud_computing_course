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
    sudo yum update
    sudo yum -y install python-pip
    sudo yum -y install python3
    sudo yum -y install git


    mkdir parking_lot
    cd parking_lot
    git clone https://github.com/guyfarhi11/cloud_computing_course.git
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r cloud_computing_course/ex1/requirements.txt

    sudo env "PATH=$PATH" python3 cloud_computing_course/ex1/app.py

""",
)

# Export the public IP of the created instance
pulumi.export('publicIp', server.public_ip)
pulumi.export('publicDns', server.public_dns)
