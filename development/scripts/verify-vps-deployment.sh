#!/bin/bash

# Script de verificación para deployment de BookGen en VPS Ubuntu IONOS
# Ejecutar después del despliegue para validar la configuración

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BOOKGEN_DIR="/opt/bookgen"
PASSED=0
FAILED=0
WARNINGS=0

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    PASSED=$((PASSED + 1))
}

print_failure() {
    echo -e "${RED}❌ $1${NC}"
    FAILED=$((FAILED + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 está instalado"
        return 0
    else
        print_failure "$1 NO está instalado"
        return 1
    fi
}

check_service() {
    if systemctl is-active --quiet $1; then
        print_success "Servicio $1 está activo"
        return 0
    else
        print_failure "Servicio $1 NO está activo"
        return 1
    fi
}

check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":$1 "; then
        print_success "Puerto $1 está abierto"
        return 0
    elif ss -tuln 2>/dev/null | grep -q ":$1 "; then
        print_success "Puerto $1 está abierto"
        return 0
    else
        print_failure "Puerto $1 NO está abierto"
        return 1
    fi
}

print_header "Verificación de Deployment BookGen VPS Ubuntu"
echo ""

# 1. Verificar prerrequisitos del sistema
print_header "1. Verificando Prerrequisitos del Sistema"
check_command docker
check_command docker-compose || check_command "docker compose"
check_command certbot
check_command ufw
check_command fail2ban-client
echo ""

# 2. Verificar estructura de directorios
print_header "2. Verificando Estructura de Directorios"
for dir in "$BOOKGEN_DIR" "$BOOKGEN_DIR/data" "$BOOKGEN_DIR/output" "$BOOKGEN_DIR/backups" "/var/log/bookgen"; do
    if [ -d "$dir" ]; then
        print_success "Directorio $dir existe"
    else
        print_failure "Directorio $dir NO existe"
    fi
done
echo ""

# 3. Verificar archivos de configuración
print_header "3. Verificando Archivos de Configuración"
for file in "$BOOKGEN_DIR/.env.production" "$BOOKGEN_DIR/docker-compose.prod.yml" "$BOOKGEN_DIR/infrastructure/nginx/nginx.conf"; do
    if [ -f "$file" ]; then
        print_success "Archivo $file existe"
    else
        print_failure "Archivo $file NO existe"
    fi
done
echo ""

# 4. Verificar servicios
print_header "4. Verificando Servicios"
check_service docker
check_service bookgen
if systemctl list-units --type=service | grep -q fail2ban; then
    check_service fail2ban
else
    print_warning "Fail2ban no está instalado como servicio"
fi
echo ""

# 5. Verificar contenedores Docker
print_header "5. Verificando Contenedores Docker"
if docker ps > /dev/null 2>&1; then
    containers=("bookgen-api-prod" "bookgen-worker-1-prod" "bookgen-worker-2-prod" "bookgen-nginx-prod")
    for container in "${containers[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            print_success "Contenedor $container está corriendo"
        else
            print_failure "Contenedor $container NO está corriendo"
        fi
    done
else
    print_failure "No se puede acceder a Docker"
fi
echo ""

# 6. Verificar puertos
print_header "6. Verificando Puertos Abiertos"
check_port 22   # SSH
check_port 80   # HTTP
check_port 443  # HTTPS
echo ""

# 7. Verificar firewall
print_header "7. Verificando Configuración de Firewall"
if ufw status | grep -q "Status: active"; then
    print_success "UFW está activo"
    
    for port in 22 80 443; do
        if ufw status | grep -q "$port"; then
            print_success "Puerto $port permitido en UFW"
        else
            print_warning "Puerto $port podría no estar permitido en UFW"
        fi
    done
else
    print_failure "UFW NO está activo"
fi
echo ""

# 8. Verificar health endpoint
print_header "8. Verificando Health Endpoint"
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "API health endpoint responde correctamente"
else
    print_failure "API health endpoint NO responde"
fi
echo ""

# 9. Verificar scripts de automatización
print_header "9. Verificando Scripts de Automatización"
for script in "$BOOKGEN_DIR/backup.sh" "$BOOKGEN_DIR/monitor.sh"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        print_success "Script $(basename $script) existe y es ejecutable"
    else
        print_failure "Script $(basename $script) falta o no es ejecutable"
    fi
done
echo ""

# 10. Verificar cron jobs
print_header "10. Verificando Cron Jobs"
if grep -q "backup.sh" /etc/crontab; then
    print_success "Backup diario programado en cron"
else
    print_failure "Backup diario NO está programado"
fi

if grep -q "monitor.sh" /etc/crontab; then
    print_success "Monitoreo programado en cron (cada 5 minutos)"
else
    print_failure "Monitoreo NO está programado"
fi
echo ""

# 11. Verificar logs
print_header "11. Verificando Sistema de Logs"
if [ -f "/var/log/bookgen/monitor.log" ]; then
    print_success "Log de monitoreo existe"
else
    print_warning "Log de monitoreo aún no existe (se creará en el primer monitoreo)"
fi

if [ -f "/etc/logrotate.d/bookgen" ]; then
    print_success "Rotación de logs configurada"
else
    print_failure "Rotación de logs NO configurada"
fi
echo ""

# 12. Verificar SSL (opcional)
print_header "12. Verificando SSL (Opcional)"
DOMAIN=$(grep -oP '(?<=server_name ).*(?=;)' $BOOKGEN_DIR/infrastructure/nginx/nginx.conf 2>/dev/null | head -1 || echo "_")
if [ "$DOMAIN" != "_" ]; then
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        print_success "Certificado SSL encontrado para $DOMAIN"
        
        # Verificar validez del certificado
        CERT_FILE="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
        if [ -f "$CERT_FILE" ]; then
            EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_FILE" 2>/dev/null | cut -d= -f2)
            print_info "Certificado expira: $EXPIRY"
        fi
    else
        print_warning "Certificado SSL no configurado para $DOMAIN"
    fi
else
    print_warning "Dominio no configurado en nginx.conf (usando '_')"
fi
echo ""

# 13. Resumen final
print_header "Resumen de Verificación"
echo ""
echo -e "${GREEN}Pruebas exitosas: $PASSED${NC}"
echo -e "${YELLOW}Advertencias: $WARNINGS${NC}"
echo -e "${RED}Pruebas fallidas: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ¡Deployment verificado exitosamente!${NC}"
    echo ""
    echo "Próximos pasos recomendados:"
    echo "1. Configurar SSL si aún no está hecho: certbot certonly --standalone -d tu-dominio.com"
    echo "2. Actualizar .env.production con tus API keys reales"
    echo "3. Reiniciar el servicio: systemctl restart bookgen"
    echo "4. Monitorear logs: tail -f /var/log/bookgen/monitor.log"
    exit 0
else
    echo -e "${RED}❌ Hay problemas que necesitan ser resueltos${NC}"
    echo ""
    echo "Revisa los errores arriba y ejecuta los siguientes comandos según sea necesario:"
    echo "- Ver logs de servicios: journalctl -u bookgen -n 50"
    echo "- Ver logs de Docker: docker-compose -f $BOOKGEN_DIR/docker-compose.prod.yml logs"
    echo "- Reejecutar deployment: sudo ./deploy-vps.sh"
    exit 1
fi
