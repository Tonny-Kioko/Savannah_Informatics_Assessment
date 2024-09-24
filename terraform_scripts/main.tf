provider "aws" {
  region = "us-east-1" 
}

# Create a key pair to SSH into the EC2 instance
resource "access_key" "secret_key" {
  key_name   = "deployer-key"
  public_key = file("~/credentials.tfvars") 
}

# Security group to allow SSH, HTTP, and required port access
resource "aws_security_group" "web_sg" {
  name        = "web-app-sg"
  description = "Allow SSH, HTTP, PostgreSQL, Prometheus, and Grafana access"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
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

# EC2 Instance
resource "aws_instance" "app_instance" {
  ami           = "ami-0c55b159cbfafe1f0"
  key_name      = aws_key_pair.access_key
  security_groups = [aws_security_group.web_sg.name]

  user_data = <<-EOF
    #!/bin/bash
    sudo apt update -y
    sudo apt install docker.io docker-compose -y
    sudo systemctl start docker
    sudo systemctl enable docker

    # Clone application repository
    git clone https://github.com/Tonny-Kioko/Savannah_Informatics_Assessment.git

    # Navigate to the app folder and run the app
    cd /home/ubuntu/app
    sudo docker-compose up -d
  EOF

  tags = {
    Name = "DjangoAppServer"
  }
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "main_vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

# Subnet
resource "aws_subnet" "main_subnet" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
}

# Route Table
resource "aws_route_table" "main_route" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "main_assoc" {
  subnet_id      = aws_subnet.main_subnet.id
  route_table_id = aws_route_table.main_route.id
}
