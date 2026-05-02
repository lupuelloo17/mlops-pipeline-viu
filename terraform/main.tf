# terraform/main.tf — Infraestructura mínima en AWS para el pipeline MLOps

terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── Data sources ───────────────────────────────────────────────────────────────

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# ── Security Group ─────────────────────────────────────────────────────────────

resource "aws_security_group" "mlops_api" {
  name        = "${var.project_name}-sg"
  description = "Permite HTTP (80) y SSH (22)"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-sg"
    Project = var.project_name
  }
}

# ── Key Pair ───────────────────────────────────────────────────────────────────

resource "aws_key_pair" "mlops" {
  key_name   = "${var.project_name}-key"
  public_key = file(var.public_key_path)
}

# ── EC2 Instance ───────────────────────────────────────────────────────────────

resource "aws_instance" "mlops_api" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.mlops.key_name
  vpc_security_group_ids = [aws_security_group.mlops_api.id]

  # Instala Docker al arrancar la instancia
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ec2-user
  EOF

  tags = {
    Name    = "${var.project_name}-api"
    Project = var.project_name
    Env     = "production"
  }
}

# ── Outputs ────────────────────────────────────────────────────────────────────

output "instance_public_ip" {
  description = "IP pública de la instancia EC2"
  value       = aws_instance.mlops_api.public_ip
}

output "api_url" {
  description = "URL de la API desplegada"
  value       = "http://${aws_instance.mlops_api.public_ip}/docs"
}

output "ssh_command" {
  description = "Comando SSH para conectar a la instancia"
  value       = "ssh -i ~/.ssh/id_rsa ec2-user@${aws_instance.mlops_api.public_ip}"
}
