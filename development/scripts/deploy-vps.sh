#!/bin/bash

# Script de despliegue para VPS Ubuntu IONOS
# Ejecutar como root o con sudo

set -e  # Salir si cualquier comando falla

echo "🚀 Iniciando despliegue de BookGen en VPS Ubuntu..."

# Variables
BOOKGEN_DIR="/opt/bookgen"
BACKUP_DIR="/opt/bookgen/backups"
SERVICE_USER="bookgen"
DOMAIN="bookgen.yourdomain.com"  # Cambiar por tu dominio real

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $USER
    systemctl enable docker
    systemctl start docker
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Instalando..."
    curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

print_status "Docker y Docker Compose están instalados"

# 2. Crear usuario del servicio si no existe
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d $BOOKGEN_DIR $SERVICE_USER
    print_status "Usuario $SERVICE_USER creado"
fi

# 3. Crear estructura de directorios
mkdir -p $BOOKGEN_DIR
mkdir -p $BACKUP_DIR
mkdir -p /var/log/bookgen
mkdir -p /etc/letsencrypt

# Directorios de datos
mkdir -p $BOOKGEN_DIR/data
mkdir -p $BOOKGEN_DIR/output
mkdir -p $BOOKGEN_DIR/sources
mkdir -p $BOOKGEN_DIR/collections
mkdir -p $BOOKGEN_DIR/templates
mkdir -p $BOOKGEN_DIR/nginx

print_status "Estructura de directorios creada"

# 4. Configurar permisos
chown -R $SERVICE_USER:$SERVICE_USER $BOOKGEN_DIR
chown -R $SERVICE_USER:$SERVICE_USER /var/log/bookgen
chmod -R 755 $BOOKGEN_DIR
chmod -R 644 $BOOKGEN_DIR/data

print_status "Permisos configurados"

# 5. Descargar archivos de configuración si no existen
cd $BOOKGEN_DIR

if [ ! -f "infrastructure/docker-compose.prod.yml" ]; then
    print_warning "Descarga docker-compose.prod.yml desde tu repositorio"
    # wget https://raw.githubusercontent.com/tuusuario/bookgen/main/infrastructure/docker-compose.prod.yml
fi

if [ ! -f "infrastructure/nginx/nginx.conf" ]; then
    print_warning "Descarga nginx.conf desde tu repositorio"
    # wget -O infrastructure/nginx/nginx.conf https://raw.githubusercontent.com/tuusuario/bookgen/main/infrastructure/nginx/nginx.conf
fi

# 6. Configurar variables de entorno
if [ ! -f ".env.production" ]; then
    print_warning "Creando archivo .env.production de ejemplo"
    cat > .env.production << EOF
ENV=production
DEBUG=false
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct
SITE_URL=https://$DOMAIN
SITE_TITLE=BookGen - Generador Automático de Biografías
DATABASE_URL=sqlite:///./data/bookgen_production.db
LOG_LEVEL=INFO
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1
CORS_ORIGINS=https://$DOMAIN
MAX_CONCURRENT_GENERATIONS=3
STORAGE_PATH=/app/data
OUTPUT_PATH=/app/docx
WORKER_POOL_SIZE=2
EOF
    print_warning "⚠️  IMPORTANTE: Edita .env.production con tus configuraciones reales"
fi

# 7. Instalar Certbot para SSL si no está instalado
if ! command -v certbot &> /dev/null; then
    print_status "Instalando Certbot para certificados SSL..."
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# 8. Instalar y configurar Fail2ban para protección SSH
if ! command -v fail2ban-client &> /dev/null; then
    print_status "Instalando Fail2ban para protección SSH..."
    apt install -y fail2ban
    
    # Crear configuración personalizada de Fail2ban
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = admin@${DOMAIN}
sendername = Fail2Ban
action = %(action_mwl)s

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/*error.log
maxretry = 5

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/*access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/*access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
filter = nginx-noproxy
logpath = /var/log/nginx/*access.log
maxretry = 2
EOF

    systemctl enable fail2ban
    systemctl start fail2ban
    print_status "Fail2ban configurado y activo"
fi

# 9. Configurar certificado SSL (comentado para primera instalación)
# print_status "Configurando certificado SSL..."
# certbot certonly --standalone -d $DOMAIN --agree-tos --no-eff-email --email admin@$DOMAIN

# 10. Configurar firewall
print_status "Configurando firewall..."
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
ufw --force enable

# 11. Crear servicio systemd para auto-inicio
cat > /etc/systemd/system/bookgen.service << EOF
[Unit]
Description=BookGen Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$BOOKGEN_DIR
ExecStart=/usr/local/bin/docker-compose -f infrastructure/docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f infrastructure/docker-compose.prod.yml down
TimeoutStartSec=0
User=$SERVICE_USER
Group=$SERVICE_USER

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable bookgen.service

print_status "Servicio systemd configurado"

# 12. Configurar rotación de logs
cat > /etc/logrotate.d/bookgen << EOF
/var/log/bookgen/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
    postrotate
        docker-compose -f $BOOKGEN_DIR/infrastructure/docker-compose.prod.yml restart bookgen-api
    endscript
}
EOF

print_status "Rotación de logs configurada"

# 13. Crear script de backup
cat > $BOOKGEN_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/bookgen/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="bookgen_backup_$DATE"

# Crear backup
mkdir -p $BACKUP_DIR/$BACKUP_NAME
cp -r /opt/bookgen/data $BACKUP_DIR/$BACKUP_NAME/
cp -r /opt/bookgen/output $BACKUP_DIR/$BACKUP_NAME/
cp /opt/bookgen/.env.production $BACKUP_DIR/$BACKUP_NAME/

# Comprimir
tar -czf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $BACKUP_DIR $BACKUP_NAME
rm -rf $BACKUP_DIR/$BACKUP_NAME

# Limpiar backups antiguos (mantener solo 7 días)
find $BACKUP_DIR -name "bookgen_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completado: $BACKUP_NAME.tar.gz"
EOF

chmod +x $BOOKGEN_DIR/backup.sh
chown $SERVICE_USER:$SERVICE_USER $BOOKGEN_DIR/backup.sh

# Configurar cron para backup diario
echo "0 2 * * * $SERVICE_USER $BOOKGEN_DIR/backup.sh" >> /etc/crontab

print_status "Script de backup configurado"

# 14. Configurar monitoreo básico
cat > $BOOKGEN_DIR/monitor.sh << 'EOF'
#!/bin/bash
# Script básico de monitoreo

HEALTH_URL="http://localhost:8000/health"
LOG_FILE="/var/log/bookgen/monitor.log"

# Verificar que el servicio esté corriendo
if curl -f -s $HEALTH_URL > /dev/null; then
    echo "$(date): ✅ BookGen API está funcionando" >> $LOG_FILE
else
    echo "$(date): ❌ BookGen API no responde, reiniciando..." >> $LOG_FILE
    cd /opt/bookgen
    docker-compose -f infrastructure/docker-compose.prod.yml restart bookgen-api
fi

# Verificar uso de disco
DISK_USAGE=$(df /opt/bookgen | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "$(date): ⚠️  Uso de disco alto: ${DISK_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x $BOOKGEN_DIR/monitor.sh
chown $SERVICE_USER:$SERVICE_USER $BOOKGEN_DIR/monitor.sh

# Configurar cron para monitoreo cada 5 minutos
echo "*/5 * * * * $SERVICE_USER $BOOKGEN_DIR/monitor.sh" >> /etc/crontab

print_status "Monitoreo configurado"

# 15. Mostrar información final
print_status "¡Despliegue inicial completado!"
echo ""
echo "📋 Pasos siguientes:"
echo "1. Edita $BOOKGEN_DIR/.env.production con tus configuraciones reales"
echo "2. Actualiza el dominio en infrastructure/nginx/nginx.conf"
echo "3. Configura el certificado SSL: certbot certonly --standalone -d $DOMAIN"
echo "4. Inicia el servicio: systemctl start bookgen"
echo "5. Verifica el estado: systemctl status bookgen"
echo ""
echo "🔧 Comandos útiles:"
echo "- Ver logs: docker-compose -f $BOOKGEN_DIR/infrastructure/docker-compose.prod.yml logs -f"
echo "- Reiniciar: systemctl restart bookgen"
echo "- Backup manual: $BOOKGEN_DIR/backup.sh"
echo "- Monitor manual: $BOOKGEN_DIR/monitor.sh"
echo ""
echo "🔐 Seguridad configurada:"
echo "- Firewall UFW activo (puertos 22, 80, 443)"
echo "- Fail2ban protegiendo SSH y Nginx"
echo "- Rate limiting en Nginx"
echo "- SSL listo para configurar"
echo ""
print_status "BookGen está listo para usar en: https://$DOMAIN"