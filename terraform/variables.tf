# terraform/variables.tf

variable "aws_region" {
  description = "Región de AWS donde se despliega la infraestructura"
  type        = string
  default     = "eu-west-1"    # Irlanda — más cercana a España
}

variable "project_name" {
  description = "Prefijo para nombrar los recursos"
  type        = string
  default     = "iris-mlops"
}

variable "instance_type" {
  description = "Tipo de instancia EC2 (t2.micro está en Free Tier)"
  type        = string
  default     = "t2.micro"
}

variable "public_key_path" {
  description = "Ruta al archivo de clave pública SSH"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "ssh_cidr" {
  description = "CIDR permitido para SSH (usa tu IP para mayor seguridad)"
  type        = string
  default     = "0.0.0.0/0"
}
