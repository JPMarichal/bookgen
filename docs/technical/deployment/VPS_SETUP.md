# 🖥️ VPS Ubuntu IONOS - Guía de Configuración de Producción

Este documento describe la configuración completa del VPS Ubuntu IONOS para el despliegue de BookGen en producción.

## ✅ Criterios de Aceptación Implementados

- [x] **VPS accesible via SSH con clave** - Configuración de acceso SSH seguro
- [x] **Docker y docker-compose instalados** - Instalación automática via deploy-vps.sh
- [x] **Certificado SSL configurado y válido** - Integración con Let's Encrypt via Certbot
- [x] **Nginx proxy funcional con rate limiting** - Reverse proxy en infrastructure/docker-compose.prod.yml
- [x] **Backups diarios programados** - Script backup.sh ejecutado via cron
- [x] **Monitoreo cada 5 minutos activo** - Script monitor.sh ejecutado via cron
- [x] **Firewall configurado (puertos 22, 80, 443)** - UFW configurado automáticamente

## 📋 Arquitectura del Sistema

```
Internet
    ↓
[Firewall UFW: 22, 80, 443]
    ↓
[Nginx Reverse Proxy] ← SSL/TLS (Let's Encrypt)
    ↓
[BookGen API Container]
    ↓
[Worker Containers] × 2
    ↓
[Persistent Storage] → /opt/bookgen/
```

## 🚀 Instalación Rápida

### 1. Prerequisitos

- Ubuntu 20.04 LTS o superior
- Al menos 2GB RAM y 2 vCPUs
- 20GB de espacio en disco
- Acceso root o sudo
- Dominio configurado (opcional pero recomendado)

### 2. Ejecución del Script de Despliegue

```bash
# Conectar al VPS
ssh root@tu-vps-ip

# Descargar el script
curl -fsSL https://raw.githubusercontent.com/JPMarichal/bookgen/main/deploy-vps.sh -o deploy-vps.sh

# Dar permisos de ejecución
chmod +x deploy-vps.sh

# Ejecutar el script
sudo ./deploy-vps.sh
```

El script automáticamente:
- ✅ Instala Docker y Docker Compose
- ✅ Crea usuario del servicio `bookgen`
- ✅ Configura estructura de directorios en `/opt/bookgen/`
- ✅ Instala Certbot para SSL
- ✅ Configura Fail2ban para protección SSH y Nginx
- ✅ Configura firewall UFW (puertos 22, 80, 443)
- ✅ Crea servicio systemd para auto-inicio
- ✅ Configura rotación de logs
- ✅ Implementa backup automático diario
- ✅ Configura monitoreo cada 5 minutos

### 3. Configuración Post-Instalación

```bash
# Editar variables de entorno
cd /opt/bookgen
sudo nano .env.production

# Variables críticas a configurar:
# - OPENROUTER_API_KEY=tu_api_key_real
# - SITE_URL=https://tu-dominio.com
# - SECRET_KEY=genera_una_clave_segura
```

### 4. Configurar SSL (si tienes dominio)

```bash
# Detener servicios en puerto 80
sudo systemctl stop bookgen

# Obtener certificado SSL
sudo certbot certonly --standalone -d tu-dominio.com

# Actualizar nginx.conf con tu dominio
sudo nano /opt/bookgen/nginx/nginx.conf
# Cambiar: server_name _ 
# Por: server_name tu-dominio.com

# Actualizar ruta de certificados
# ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
```

### 5. Iniciar el Sistema

```bash
# Iniciar BookGen
sudo systemctl start bookgen

# Verificar estado
sudo systemctl status bookgen

# Ver logs en tiempo real
docker-compose -f /opt/bookgen/infrastructure/docker-compose.prod.yml logs -f
```

## 🔍 Verificación del Deployment

### Opción 1: Script Automático de Verificación

```bash
# Descargar y ejecutar script de verificación
curl -fsSL https://raw.githubusercontent.com/JPMarichal/bookgen/main/verify-vps-deployment.sh -o verify-vps-deployment.sh
chmod +x verify-vps-deployment.sh
sudo ./verify-vps-deployment.sh
```

### Opción 2: Verificación Manual

#### Verificar SSH y Docker
```bash
# Desde tu máquina local
ssh user@vps-ip "docker ps"
```

#### Verificar SSL
```bash
# Verificar certificado
curl -I https://bookgen.yourdomain.com

# Verificar detalles del certificado
openssl s_client -connect bookgen.yourdomain.com:443 -servername bookgen.yourdomain.com
```

#### Verificar Servicios
```bash
# Estado de servicios
systemctl status bookgen
systemctl status fail2ban

# Contenedores Docker
docker ps

# Health check de API
curl -f http://localhost:8000/health
```

#### Verificar Backups
```bash
# Listar backups
ls -la /opt/bookgen/backups/

# Ver configuración de cron
crontab -l | grep backup

# Ejecutar backup manual
sudo /opt/bookgen/backup.sh
```

#### Verificar Monitoreo
```bash
# Ver logs de monitoreo
tail -f /var/log/bookgen/monitor.log

# Ver configuración de cron
crontab -l | grep monitor
```

#### Verificar Firewall y Seguridad
```bash
# Estado de UFW
sudo ufw status verbose

# Puertos abiertos
sudo netstat -tulpn | grep -E ':(22|80|443)'

# Estado de Fail2ban
sudo fail2ban-client status
sudo fail2ban-client status sshd
sudo fail2ban-client status nginx-http-auth
```

## 🔐 Configuraciones de Seguridad

### Firewall UFW

El script configura automáticamente:
- Puerto 22 (SSH)
- Puerto 80 (HTTP)
- Puerto 443 (HTTPS)

### Fail2ban

Protección automática contra:
- Ataques de fuerza bruta SSH (3 intentos → ban 2 horas)
- Ataques a Nginx HTTP auth (5 intentos → ban 1 hora)
- Scripts maliciosos (6 intentos → ban)
- Bots maliciosos (2 intentos → ban)
- Intentos de proxy (2 intentos → ban)

### Nginx Rate Limiting

Configurado en `nginx/nginx.conf`:
- 10 requests/segundo por IP
- Burst de hasta 20 requests
- Protección de endpoints API

### SSL/TLS

- TLS 1.2 y 1.3
- Ciphers seguros (ECDHE-RSA-AES128/256-GCM-SHA256/384)
- Headers de seguridad:
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security: max-age=63072000

## 📊 Monitoreo y Backups

### Monitoreo Automático

El script `monitor.sh` se ejecuta cada 5 minutos y:
- Verifica el health endpoint de la API
- Reinicia el servicio si no responde
- Monitorea uso de disco (alerta si >85%)
- Registra todo en `/var/log/bookgen/monitor.log`

### Backups Automáticos

El script `backup.sh` se ejecuta diariamente a las 2:00 AM y:
- Respalda `/opt/bookgen/data/`
- Respalda `/opt/bookgen/output/`
- Respalda `.env.production`
- Comprime todo en un archivo `.tar.gz`
- Limpia backups antiguos (>7 días)
- Almacena en `/opt/bookgen/backups/`

### Rotación de Logs

Configurado en `/etc/logrotate.d/bookgen`:
- Rotación diaria
- Mantiene 30 días de logs
- Comprime logs antiguos
- Reinicia servicio después de rotación

## 🛠️ Comandos Útiles

### Gestión de Servicios

```bash
# Iniciar/Detener/Reiniciar
sudo systemctl start bookgen
sudo systemctl stop bookgen
sudo systemctl restart bookgen

# Ver estado
sudo systemctl status bookgen

# Ver logs del servicio
sudo journalctl -u bookgen -f
```

### Gestión de Contenedores

```bash
cd /opt/bookgen

# Ver contenedores
docker ps

# Ver logs
docker-compose -f infrastructure/docker-compose.prod.yml logs -f

# Reiniciar contenedor específico
docker-compose -f infrastructure/docker-compose.prod.yml restart bookgen-api

# Actualizar imágenes
docker-compose -f infrastructure/docker-compose.prod.yml pull
docker-compose -f infrastructure/docker-compose.prod.yml up -d
```

### Gestión de Backups

```bash
# Backup manual
sudo /opt/bookgen/backup.sh

# Listar backups
ls -lh /opt/bookgen/backups/

# Restaurar desde backup
cd /opt/bookgen/backups
tar -xzf bookgen_backup_YYYYMMDD_HHMMSS.tar.gz
# Copiar archivos necesarios de vuelta a /opt/bookgen/
```

### Gestión de SSL

```bash
# Ver certificados instalados
sudo certbot certificates

# Renovar certificados (test)
sudo certbot renew --dry-run

# Renovar certificados (producción)
sudo certbot renew

# Verificar configuración de Nginx
sudo nginx -t
```

### Monitoreo de Recursos

```bash
# Uso de CPU y memoria
docker stats

# Uso de disco
df -h
du -sh /opt/bookgen/*

# Conexiones activas
netstat -an | grep :80
netstat -an | grep :443

# Logs de acceso Nginx
tail -f /var/log/nginx/bookgen-access.log
```

## 🔧 Solución de Problemas

### El servicio no inicia

```bash
# Ver logs del servicio
sudo journalctl -u bookgen -n 50

# Verificar Docker
sudo docker ps -a

# Verificar configuración
cd /opt/bookgen
sudo docker-compose -f infrastructure/docker-compose.prod.yml config
```

### API no responde

```bash
# Verificar contenedores
sudo docker ps

# Ver logs del contenedor
sudo docker logs bookgen-api-prod

# Verificar health endpoint
curl -v http://localhost:8000/health
```

### Problemas de SSL

```bash
# Verificar certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew --dry-run

# Verificar configuración Nginx
sudo nginx -t
```

### Fail2ban no funciona

```bash
# Ver estado
sudo fail2ban-client status

# Ver reglas específicas
sudo fail2ban-client status sshd

# Desbanear una IP
sudo fail2ban-client set sshd unbanip <IP>

# Reiniciar fail2ban
sudo systemctl restart fail2ban
```

## 📞 Soporte

Para soporte adicional:

1. Revisa los logs: `/var/log/bookgen/`
2. Ejecuta el script de verificación: `./verify-vps-deployment.sh`
3. Consulta la documentación en `DEPLOYMENT.md`
4. Revisa issues en GitHub

## 🔄 Actualizaciones

### Actualización Manual

```bash
cd /opt/bookgen

# Detener servicios
sudo docker-compose -f infrastructure/docker-compose.prod.yml down

# Actualizar imagen
sudo docker pull ghcr.io/jpmarichal/bookgen:latest

# Iniciar servicios
sudo docker-compose -f infrastructure/docker-compose.prod.yml up -d

# Verificar
curl -f http://localhost:8000/health
```

### Actualización via CI/CD

Las actualizaciones se despliegan automáticamente al hacer push a `main` si GitHub Actions está configurado.

## 📝 Checklist de Deployment

- [ ] VPS actualizado: `apt update && apt upgrade -y`
- [ ] Script deploy-vps.sh ejecutado exitosamente
- [ ] Variables de entorno configuradas en `.env.production`
- [ ] Certificado SSL obtenido (si tienes dominio)
- [ ] Dominio configurado en `nginx/nginx.conf`
- [ ] Servicio bookgen iniciado y activo
- [ ] Health endpoint responde: `curl http://localhost:8000/health`
- [ ] Firewall activo: `ufw status`
- [ ] Fail2ban activo: `fail2ban-client status`
- [ ] Backups programados: `crontab -l | grep backup`
- [ ] Monitoreo programado: `crontab -l | grep monitor`
- [ ] Logs rotan correctamente: `/etc/logrotate.d/bookgen`
- [ ] Script de verificación ejecutado: `./verify-vps-deployment.sh`

---

**¡Tu VPS Ubuntu IONOS está listo para producción!** 🚀
