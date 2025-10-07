# Guía de Despliegue BookGen - VPS Ubuntu IONOS

Esta guía te ayudará a desplegar BookGen en tu VPS Ubuntu de IONOS con Docker y configurar el pipeline de CI/CD con GitHub Actions.

## 📋 Prerrequisitos

### Entorno de Desarrollo (Windows 11)
- ✅ Docker Desktop instalado
- ✅ VS Code con extensiones necesarias
- ✅ GitHub Copilot configurado
- ✅ Git configurado con tu cuenta de GitHub

### VPS Ubuntu IONOS
- Ubuntu 20.04 LTS o superior
- Al menos 2GB RAM y 2 vCPUs
- 20GB de espacio en disco
- Acceso SSH root o sudo
- Dominio configurado (opcional pero recomendado)

## 🚀 Proceso de Despliegue

### 1. Configuración Inicial del VPS

```bash
# Conectar al VPS vía SSH
ssh root@tu-vps-ip

# Actualizar sistema
apt update && apt upgrade -y

# Crear usuario para deployment (opcional)
adduser deploy
usermod -aG sudo deploy
```

### 2. Ejecución del Script de Despliegue

```bash
# Descargar y ejecutar el script de despliegue
curl -fsSL https://raw.githubusercontent.com/tu-usuario/bookgen/main/deploy-vps.sh -o deploy-vps.sh
chmod +x deploy-vps.sh
sudo ./deploy-vps.sh
```

El script automáticamente:
- ✅ Instala Docker y Docker Compose
- ✅ Crea la estructura de directorios
- ✅ Configura el usuario del servicio
- ✅ Instala Certbot para SSL
- ✅ Configura firewall básico
- ✅ Crea servicios systemd
- ✅ Configura rotación de logs
- ✅ Implementa backup automático
- ✅ Configura monitoreo básico

### 3. Configuración Post-Instalación

#### 3.1 Variables de Entorno
```bash
cd /opt/bookgen
nano .env.production
```

Actualiza las siguientes variables:
```env
OPENROUTER_API_KEY=tu_api_key_real_aqui
SITE_URL=https://tu-dominio.com
ALLOWED_HOSTS=tu-dominio.com,localhost
CORS_ORIGINS=https://tu-dominio.com
SECRET_KEY=tu_clave_secreta_muy_segura
```

#### 3.2 Configuración SSL (si tienes dominio)
```bash
# Detener cualquier servicio en puerto 80
sudo systemctl stop nginx

# Obtener certificado
sudo certbot certonly --standalone -d tu-dominio.com

# Actualizar nginx.conf con tu dominio
nano /opt/bookgen/nginx/nginx.conf
```

### 4. Configuración de GitHub Actions

#### 4.1 Secrets del Repositorio
En tu repositorio de GitHub, ve a Settings > Secrets and variables > Actions y añade:

```
VPS_HOST=tu-vps-ip
VPS_USER=root
VPS_SSH_KEY=tu-clave-ssh-privada
OPENROUTER_API_KEY=tu-api-key
SITE_URL=https://tu-dominio.com
SITE_TITLE=BookGen - Tu Título
```

#### 4.2 Clave SSH para Despliegue
```bash
# En tu VPS, generar clave para GitHub Actions
ssh-keygen -t ed25519 -C "github-actions@bookgen"

# Añadir la clave pública a authorized_keys
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys

# Copiar la clave privada para GitHub Secrets
cat ~/.ssh/id_ed25519
```

### 5. Iniciar el Sistema

```bash
# Iniciar BookGen
sudo systemctl start bookgen

# Verificar estado
sudo systemctl status bookgen

# Ver logs
cd /opt/bookgen
docker-compose -f docker-compose.prod.yml logs -f
```

## 📊 Monitoreo y Mantenimiento

### Comandos Útiles

```bash
# Estado del sistema
sudo systemctl status bookgen

# Ver logs en tiempo real
cd /opt/bookgen
docker-compose -f docker-compose.prod.yml logs -f bookgen-api

# Reiniciar servicios
sudo systemctl restart bookgen

# Backup manual
sudo /opt/bookgen/backup.sh

# Verificar salud del sistema
curl -f http://localhost:8000/health

# Ver uso de recursos
docker stats

# Limpiar imágenes no utilizadas
docker image prune -f
```

### Logs Importantes

```bash
# Logs de aplicación
tail -f /var/log/bookgen/bookgen.log

# Logs de monitoreo
tail -f /var/log/bookgen/monitor.log

# Logs de Nginx
tail -f /var/log/nginx/bookgen-access.log
tail -f /var/log/nginx/bookgen-error.log

# Logs de sistema
journalctl -u bookgen -f
```

### Backups

Los backups se ejecutan automáticamente todos los días a las 2:00 AM y se almacenan en `/opt/bookgen/backups/`. 

```bash
# Listar backups disponibles
ls -la /opt/bookgen/backups/

# Restaurar desde backup
cd /opt/bookgen/backups
tar -xzf bookgen_backup_YYYYMMDD_HHMMSS.tar.gz
# Copiar archivos necesarios...
```

## 🔧 Solución de Problemas

### El servicio no inicia
```bash
# Verificar logs
sudo journalctl -u bookgen -n 50

# Verificar Docker
sudo docker ps -a

# Verificar configuración
cd /opt/bookgen
sudo docker-compose -f docker-compose.prod.yml config
```

### API no responde
```bash
# Verificar contenedores
sudo docker ps

# Verificar logs del contenedor
sudo docker logs bookgen-api-prod

# Verificar conectividad
curl -v http://localhost:8000/health
```

### Problemas de SSL
```bash
# Verificar certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew --dry-run

# Verificar configuración de Nginx
sudo nginx -t
```

### Alto uso de recursos
```bash
# Verificar uso de CPU y memoria
top
htop

# Verificar uso de disco
df -h
du -sh /opt/bookgen/*

# Limpiar archivos temporales
sudo docker system prune -f
```

## 🔄 Actualizaciones

### Actualización Manual
```bash
cd /opt/bookgen

# Detener servicios
sudo docker-compose -f docker-compose.prod.yml down

# Actualizar imagen
sudo docker pull ghcr.io/tu-usuario/bookgen:latest

# Iniciar servicios
sudo docker-compose -f docker-compose.prod.yml up -d

# Verificar
curl -f http://localhost:8000/health
```

### Actualización via GitHub Actions
Las actualizaciones se despliegan automáticamente cuando haces push a la rama `main`. El pipeline:

1. ✅ Ejecuta tests
2. ✅ Construye nueva imagen Docker
3. ✅ La sube a GitHub Container Registry
4. ✅ Se conecta al VPS via SSH
5. ✅ Actualiza la aplicación
6. ✅ Verifica que todo funcione

## 📞 Soporte

Si necesitas ayuda:

1. Revisa los logs primero
2. Consulta la sección de solución de problemas
3. Verifica la configuración en `.env.production`
4. Asegúrate de que los secrets de GitHub estén configurados correctamente

## 🔐 Seguridad

### Configuración Recomendada

```bash
# Cambiar puerto SSH por defecto
nano /etc/ssh/sshd_config
# Port 2222

# Desactivar login root via SSH
# PermitRootLogin no

# Configurar fail2ban
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Actualizar sistema regularmente
apt update && apt upgrade -y
```

### Backup de Seguridad

```bash
# Backup completo del sistema
rsync -avz /opt/bookgen/ usuario@servidor-backup:/backups/bookgen/

# Backup de base de datos
cp /opt/bookgen/data/bookgen_production.db /opt/bookgen/backups/
```

---

¡BookGen está listo para generar biografías automáticamente en tu VPS Ubuntu! 🚀📚