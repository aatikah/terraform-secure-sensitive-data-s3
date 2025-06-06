# For Detailed Step by Step Guide
You can find detailed step by step guide on creating this project on the [Medium post I created HERE](https://towardsaws.com/securing-aws-s3-buckets-with-terraform-a-step-by-step-guide-e17eba38266f?sk=4907c9b15f5c13ddb61582e874927dbe).

# Securing Sensitive Financial Reports in S3 Buckets: A Step-by-Step Guide

This project demonstrates how to secure an AWS S3 bucket containing sensitive files using Terraform, AWS Lambda, IAM Roles & Policy, presigned URLs and other AWS services. The setup ensures that customers can securely download their data while maintaining strict access controls, encryption, and compliance.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Deployment Steps](#deployment-steps)
- [Testing](#testing)
- [Code Structure](#code-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides a secure way to store and share sensitive files in an S3 bucket. The solution includes:
- **Server-Side Encryption**: Ensures data is encrypted at rest using AES256.
- **Block Public Access**: Prevents unauthorized public access to the bucket.
- **VPC Endpoint**: Restricts access to the S3 bucket to a specific VPC.
- **Presigned URLs**: Allows temporary, secure access to S3 objects via AWS Lambda.

## Features

- **Terraform Automation**: Infrastructure as Code (IaC) for deploying AWS resources.
- **Lambda Function**: Generates presigned URLs for secure access to S3 objects.
- **S3 Security Best Practices**: Encryption, versioning, and public access blocking.
- **Testing Script**: Validates the functionality of the deployed infrastructure.

## Prerequisites

Before deploying the project, ensure you have the following:
1. **AWS Account**: An active AWS account with sufficient permissions to create S3 buckets, Lambda functions, and IAM roles.
2. **Terraform Installed**: Terraform CLI installed on your local machine. Download it from [here](https://www.terraform.io/downloads.html).
3. **AWS CLI**: Configured with your AWS credentials. Follow the [AWS CLI setup guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).
4. **Python 3.8**: For running the Lambda function and test script.

## Deployment Steps

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/your-username/secure-s3-bucket.git
cd secure-s3-bucket
```
### 2. Initialize Terraform
Navigate to the Terraform directory and initialize Terraform:
```bash
cd terraform
terraform init
```
### 3. Update terraform.tfvars
Update the terraform.tfvars file with your VPC ID and AWS region:
```bash
vpc_id     = "your-vpc-id"
aws_region = "your-aws-region"
```
### 4. Deploy the Infrastructure
Initialize and apply the Terraform configuration to deploy the infrastructure:
```bash
terraform init
terraform validate
terraform apply -auto-approve
```
### 5. Create Python script for  Lambda Function
Create a script and name it lambda_function.py, zip and name presigned_url_function.zip


## Testing
### 1. Run the Test Script
Navigate to the test-script and run the test script:
```bash
cd ../test-script
python test.py
```
### 2. Validate Output
The script will test:

- S3 bucket access and encryption.

- Public access blocking.

- HTTPS enforcement.

- VPC endpoint restrictions.

- Lambda function for generating presigned URLs.



## Code Structure
```bash
secure-s3-bucket/
├── terraform/                  # Terraform configuration files
│   ├── main.tf                 # Main Terraform configuration
│   ├── terraform.tfvars        # Terraform variables
│   ├── lambda_function.py      # Python script for generating presigned URLs using Lambda function
│   ├── test.py                 # Python script to test the deployment
```


## Contributing
Contributions are welcome! If you have suggestions or improvements, please open an issue or submit a pull request.


## License
This project is licensed under the MIT License.


### Notes:
- Replace `your-username` in the `git clone` command with your GitHub username.
- Update the `terraform.tfvars` file with your specific AWS VPC ID and region.
- Ensure the Lambda function name (`generate-presigned-url`) matches the one in your Terraform configuration.

  ---

**⭐ If you find this project helpful, please give it a star!**
- Support me- [buymeacoffee.com/aatikah](https://buymeacoffee.com/aatikah)
- Connect with me on LinkedIn: [LinkedIn Profile](https://www.linkedin.com/in/abdulhakeem-sulaiman/)
