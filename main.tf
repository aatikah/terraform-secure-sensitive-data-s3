terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.84.0"
    }
  }
}

provider "aws" {
  # Configuration options
  profile = "default"
  region  = "us-east-1"
}



# Configure the S3 bucket with security best practices
resource "aws_s3_bucket" "statements-bucket" {
  bucket        = "statements-bucket-21321"
  force_destroy = true

  tags = {
    Name        = "Bank Statement Bucket"
    Environment = "Production"
  }

}

#Bucket versioning
resource "aws_s3_bucket_versioning" "bucket-versioning" {
  bucket = aws_s3_bucket.statements-bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure Lifecycle Rules
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle_rules" {
  bucket = aws_s3_bucket.statements-bucket.id

  # Rule 1: Transition non-current versions to Standard-IA after 30 days
  rule {
    id     = "transition_old_versions"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }
  }

  # Rule 2: Delete non-current versions after 90 days
  rule {
    id     = "delete_old_versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }

  # Rule 3: Clean up incomplete multipart uploads after 7 days
  rule {
    id     = "abort_incomplete_uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # Rule 4: Add delete markers for expired object versions
  rule {
    id     = "expire_delete_markers"
    status = "Enabled"

    expiration {
      expired_object_delete_marker = true
    }
  }
}

# Force encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "bucket-encrypt" {
  bucket = aws_s3_bucket.statements-bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Uploading an object
resource "aws_s3_object" "s3-object" {
  bucket = aws_s3_bucket.statements-bucket.id
  key    = "test-file.txt"
  source = "./test-file.txt"

}

# Block all public access by default
resource "aws_s3_bucket_public_access_block" "statements-bucket" {
  bucket = aws_s3_bucket.statements-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# # VPC Endpoint for S3
resource "aws_vpc_endpoint" "s3-endpoint" {
  vpc_id       = var.vpc_id
  service_name = "com.amazonaws.${var.aws_region}.s3"

  tags = {
    Name        = "Bank Statement Bucket"
    Environment = "Production"
  }
}

# Bucket policy to enforce HTTPS and limit access to specific VPC endpoints
resource "aws_s3_bucket_policy" "financial_reports" {
  bucket = aws_s3_bucket.statements-bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnforceHTTPSOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          "${aws_s3_bucket.statements-bucket.arn}/*",
          aws_s3_bucket.statements-bucket.arn
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" : "false"
          }
        }
      },
      {
        Sid       = "AllowVPCEndpointAccess"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          "${aws_s3_bucket.statements-bucket.arn}/*",
          aws_s3_bucket.statements-bucket.arn
        ]
        Condition = {
          StringEquals = {
            "aws:SourceVpce" : aws_vpc_endpoint.s3-endpoint.id
          }
        }
      }
    ]
  })

  depends_on = [
    aws_vpc_endpoint.s3-endpoint

  ]
}

 # Declare the IAM role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
  
}

resource "aws_iam_role_policy" "lambda_s3_access" {
  name = "lambda-s3-access-policy"
  role = aws_iam_role.lambda_exec.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.statements-bucket.arn}/*"
      }
    ]
  })
}



# Lambda function to generate presigned URLs
resource "aws_lambda_function" "presigned_url_generator" {
  filename      = "presigned_url_function.zip"
  function_name = "generate-presigned-url"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.statements-bucket.id
      URL_EXPIRY  = "3600" # URL expires in 1 hour
    }
  }
}
