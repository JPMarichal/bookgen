# GitHub Actions CI/CD Pipeline

This repository uses GitHub Actions for automated testing, building, and deployment.

## Workflows

### 1. Test Workflow (`test.yml`)
Runs on every pull request to validate code quality.

**Triggers:**
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**
- Lint code with flake8
- Check code formatting with black
- Run pytest with coverage
- Upload coverage to Codecov

### 2. CI/CD Pipeline (`ci-cd.yml`)
Complete pipeline for testing, building, and deploying the application.

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main`
- Release publications
- Manual workflow dispatch

**Jobs:**
1. **Test** - Runs linting and tests
2. **Build and Push** - Builds Docker image and pushes to GitHub Container Registry
3. **Deploy to Production** - Deploys to VPS (only on main branch)
4. **Notify** - Sends deployment status notifications

## Required GitHub Secrets

Configure these secrets in your repository settings (Settings → Secrets and variables → Actions):

### VPS Deployment Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `VPS_HOST` | VPS server hostname or IP address | `your-vps.ionos.com` or `192.168.1.100` |
| `VPS_USER` | SSH username for VPS | `bookgen` or `root` |
| `VPS_SSH_KEY` | Private SSH key for authentication | Contents of `~/.ssh/id_rsa` |
| `VPS_PORT` | SSH port (optional, defaults to 22) | `22` |

### Application Secrets (Optional)

These are optional and can be configured in `.env.production` on the VPS instead:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `OPENROUTER_API_KEY` | OpenRouter API key for AI models | `sk-or-v1-...` |
| `SITE_URL` | Production URL | `bookgen.yourdomain.com` |
| `SITE_TITLE` | Application title | `BookGen - AI Biography Generator` |

### GitHub Token

The `GITHUB_TOKEN` is automatically provided by GitHub Actions and doesn't need to be configured.

## Setting Up SSH Key for VPS Deployment

1. **Generate SSH key pair (if you don't have one):**
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-bookgen"
   ```

2. **Copy public key to VPS:**
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519.pub bookgen@your-vps.com
   ```

3. **Add private key to GitHub Secrets:**
   ```bash
   # Display private key
   cat ~/.ssh/id_ed25519
   # Copy the entire output (including BEGIN and END lines)
   # Add it to GitHub Secrets as VPS_SSH_KEY
   ```

4. **Test SSH connection:**
   ```bash
   ssh -i ~/.ssh/id_ed25519 bookgen@your-vps.com
   ```

## VPS Prerequisites

Before the first deployment, ensure your VPS has:

1. **Docker and Docker Compose installed**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

2. **BookGen directory structure:**
   ```bash
   sudo mkdir -p /opt/bookgen
   sudo chown bookgen:bookgen /opt/bookgen
   cd /opt/bookgen
   ```

3. **Docker Compose production file:**
   ```bash
   # Copy docker-compose.prod.yml to /opt/bookgen/
   wget https://raw.githubusercontent.com/jpmarichal/bookgen/main/docker-compose.prod.yml
   ```

4. **User has Docker permissions:**
   ```bash
   sudo usermod -aG docker bookgen
   # Log out and back in for changes to take effect
   ```

5. **Firewall configured:**
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

## Deployment Process

### Automatic Deployment (on push to main)

1. Developer pushes code to `main` branch
2. GitHub Actions runs tests
3. If tests pass, builds Docker image
4. Pushes image to GitHub Container Registry
5. SSHs to VPS and deploys new version
6. Performs health checks
7. Rolls back if health checks fail

### Manual Deployment

You can manually trigger the workflow from GitHub:
1. Go to Actions tab
2. Select "BookGen CI/CD Pipeline"
3. Click "Run workflow"
4. Select branch and run

### Rollback Procedure

If deployment fails, the workflow automatically attempts rollback. For manual rollback:

```bash
# SSH to VPS
ssh bookgen@your-vps.com

# Go to bookgen directory
cd /opt/bookgen

# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Pull previous image (tag with version)
docker pull ghcr.io/jpmarichal/bookgen:previous-tag

# Update docker-compose.prod.yml to use previous tag
# Then restart
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring Deployments

### View Workflow Runs
1. Go to repository's Actions tab
2. Select a workflow run to see details
3. Click on jobs to see logs

### Check Deployment Status
```bash
# Check if services are running
ssh bookgen@your-vps.com "docker ps"

# View logs
ssh bookgen@your-vps.com "docker-compose -f /opt/bookgen/docker-compose.prod.yml logs -f"

# Health check
curl -f https://bookgen.yourdomain.com/health
```

## Troubleshooting

### Build Fails

**Issue:** Docker build fails
- Check Dockerfile syntax
- Ensure all dependencies are in requirements.txt
- Review build logs in GitHub Actions

### Tests Fail

**Issue:** Tests don't pass
- Run tests locally: `pytest tests/`
- Check for missing dependencies
- Verify Python version compatibility

### Deployment Fails

**Issue:** SSH connection fails
- Verify VPS_HOST is correct
- Check VPS_SSH_KEY is complete (including BEGIN/END lines)
- Ensure VPS user has Docker permissions
- Check VPS firewall allows SSH (port 22)

**Issue:** Health check fails
- SSH to VPS and check container logs
- Verify all environment variables are set
- Check if port 8000 is accessible
- Review application logs

### Image Pull Fails

**Issue:** Cannot pull from GitHub Container Registry
- Ensure GITHUB_TOKEN has package:write permission
- Check if image was pushed successfully
- Verify image name matches repository

## Security Best Practices

1. **Never commit secrets** - Use GitHub Secrets only
2. **Rotate SSH keys** regularly
3. **Use non-root user** on VPS for deployment
4. **Enable UFW firewall** on VPS
5. **Keep dependencies updated** - Dependabot alerts
6. **Review workflow logs** for sensitive data before making public

## Support

For issues or questions:
- Check GitHub Actions logs
- Review this documentation
- Check VPS logs: `journalctl -u docker`
- Open an issue in the repository
