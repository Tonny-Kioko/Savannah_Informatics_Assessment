terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.7.0"
    }
  }
}

provider "aws" {
  region     = "us-east-1"
  access_key = var.access_key
  secret_key = var.secret_key
}

# Task Manager VPC
resource "aws_vpc" "task_manager_vpc" {
  cidr_block = "10.0.0.0/16"
}

# Public Subnet for the Presentation Layer
resource "aws_subnet" "task_manager_public_subnet" {
  vpc_id     = aws_vpc.task_manager_vpc.id
  cidr_block = "10.0.1.0/24"
}

# Private Subnet for the Data and Logic Layers
resource "aws_subnet" "task_manager_private_subnet" {
  vpc_id     = aws_vpc.task_manager_vpc.id
  cidr_block = "10.0.2.0/24"
}

# Internet Gateway
resource "aws_internet_gateway" "task_manager_igw" {
  vpc_id = aws_vpc.task_manager_vpc.id
}

# Public Route Table
resource "aws_route_table" "task_manager_public_rt" {
  vpc_id = aws_vpc.task_manager_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.task_manager_igw.id
  }
}

# Associate Public Subnet with Public Route Table
resource "aws_route_table_association" "task_manager_public_rt_association" {
  subnet_id      = aws_subnet.task_manager_public_subnet.id
  route_table_id = aws_route_table.task_manager_public_rt.id
}

# NAT Gateway and Elastic IP for Private Subnet
resource "aws_eip" "task_manager_eip" {
  vpc = true
}

resource "aws_nat_gateway" "task_manager_nat_gateway" {
  subnet_id     = aws_subnet.task_manager_public_subnet.id
  allocation_id = aws_eip.task_manager_eip.id
}

# Private Route Table
resource "aws_route_table" "task_manager_private_rt" {
  vpc_id = aws_vpc.task_manager_vpc.id

  route {
    destination_cidr_block = "0.0.0.0/0"
    nat_gateway_id         = aws_nat_gateway.task_manager_nat_gateway.id
  }
}

# Associate Private Subnet with Private Route Table
resource "aws_route_table_association" "task_manager_private_rt_association" {
  subnet_id      = aws_subnet.task_manager_private_subnet.id
  route_table_id = aws_route_table.task_manager_private_rt.id
}

# Security Group Config
resource "aws_security_group" "task_manager_sg" {
  name        = "task_manager_sg"
  description = "Allowing Inbound traffic on ports 22 and 80"
  vpc_id      = aws_vpc.task_manager_vpc.id

  ingress {
    description = "SSH traffic"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance in the Private Subnet
resource "aws_instance" "task_manager_server" {
  ami                         = "ami-0cf10cdf9fcd62d37"
  instance_type               = "t2.micro"
  subnet_id                   = aws_subnet.task_manager_private_subnet.id
  associate_public_ip_address = false
  security_groups             = [aws_security_group.task_manager_sg.id]
}

# Auto Scaling Group
resource "aws_autoscaling_group" "task_manager_asg" {
  launch_configuration = aws_launch_configuration.task_manager_lc.id
  min_size             = 1
  max_size             = 3
  desired_capacity     = 2
  vpc_zone_identifier  = [
    aws_subnet.task_manager_public_subnet.id,
    aws_subnet.task_manager_private_subnet.id
  ]
}

# Launch Configuration
resource "aws_launch_configuration" "task_manager_lc" {
  name          = "task_manager_lc"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"

  lifecycle {
    create_before_destroy = true
  }
}

# Latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"]  # Canonical
}

# S3 Bucket for Task Images
resource "aws_s3_bucket" "task_manager_s3" {
  bucket = "task-manager-savannah7521"
  tags = {
    Environment = "production"
  }
}

# S3 Bucket Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "task_manager_s3_lifecycle" {
  bucket = aws_s3_bucket.task_manager_s3.id

  rule {
    id = "uploads"
    filter {
      prefix = "task_images/"
    }
    status = "Enabled"

    expiration {
      days = 90
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }
  }
}

# CloudWatch Metric Alarm for CPU Utilization
resource "aws_cloudwatch_metric_alarm" "task_manager_cpu_alarm" {
  alarm_name          = "task_manager_cpu_alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 120
  statistic           = "Average"
  threshold           = 80
}
