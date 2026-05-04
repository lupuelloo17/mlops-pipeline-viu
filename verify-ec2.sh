#!/usr/bin/env bash
# verify-ec2.sh — comprueba que tu EC2 está lista para recibir el deploy.
#
# Uso:
#   ./verify-ec2.sh <IP_EC2>
#
# Ejemplo:
#   ./verify-ec2.sh 54.123.45.67

set -e

IP="${1:-}"
KEY="${KEY_PATH:-../mlops-key.pem}"
USER="ec2-user"

if [ -z "$IP" ]; then
  echo "Uso: $0 <IP_EC2>"
  echo "  (también puedes definir KEY_PATH=/ruta/key.pem si tu .pem no está en ../)"
  exit 1
fi

if [ ! -f "$KEY" ]; then
  echo "❌ No encuentro la clave en: $KEY"
  echo "   Define KEY_PATH=/ruta/al/.pem y vuelve a lanzar."
  exit 1
fi

chmod 400 "$KEY"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Verificando EC2 $IP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Puerto 22 abierto
echo "▶ 1/4  Puerto 22 (SSH) accesible..."
if nc -z -G 5 "$IP" 22 2>/dev/null; then
  echo "   ✅ Puerto 22 abierto"
else
  echo "   ❌ Puerto 22 cerrado o IP mala"
  exit 1
fi

# 2. Conexión SSH
echo "▶ 2/4  Conexión SSH funciona..."
if ssh -i "$KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
       "$USER@$IP" "echo ok" >/dev/null 2>&1; then
  echo "   ✅ SSH OK como $USER"
else
  echo "   ❌ SSH falla — revisa key y usuario"
  exit 1
fi

# 3. Docker instalado
echo "▶ 3/4  Docker instalado en la EC2..."
DOCKER_VERSION=$(ssh -i "$KEY" -o StrictHostKeyChecking=no \
  "$USER@$IP" "sudo docker --version 2>/dev/null || echo NO")
if [[ "$DOCKER_VERSION" == NO* ]]; then
  echo "   ⚠️  Docker NO está instalado. Instalando..."
  ssh -i "$KEY" -o StrictHostKeyChecking=no "$USER@$IP" "
    sudo yum update -y &&
    sudo yum install -y docker &&
    sudo systemctl enable --now docker &&
    sudo usermod -aG docker $USER
  "
  echo "   ✅ Docker instalado"
else
  echo "   ✅ $DOCKER_VERSION"
fi

# 4. Puerto 80 accesible desde internet
echo "▶ 4/4  Puerto 80 (HTTP) abierto desde fuera..."
if nc -z -G 5 "$IP" 80 2>/dev/null; then
  echo "   ✅ Puerto 80 abierto en el Security Group"
else
  echo "   ⚠️  Puerto 80 cerrado. Ábrelo en el Security Group:"
  echo "       Inbound rule → HTTP, TCP, 80, Source 0.0.0.0/0"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " EC2 lista. Ahora dispara el workflow CD desde GitHub."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
