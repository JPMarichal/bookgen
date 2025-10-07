# GitHub Secrets Configuration Template

Copy this checklist when configuring your GitHub repository secrets.

## Required Secrets

Navigate to: `https://github.com/JPMarichal/bookgen/settings/secrets/actions`

### 1. VPS_HOST
- **Description**: VPS hostname or IP address
- **Example**: `your-vps.ionos.com` or `192.168.1.100`
- **Value**: `_____________________________________`
- Status: ☐ Configured

### 2. VPS_USER
- **Description**: SSH username for VPS
- **Example**: `bookgen` or `root`
- **Value**: `_____________________________________`
- Status: ☐ Configured

### 3. VPS_SSH_KEY
- **Description**: Private SSH key for authentication
- **How to get**: 
  ```bash
  cat ~/.ssh/id_ed25519
  # OR generate new key:
  ssh-keygen -t ed25519 -C "github-actions-bookgen"
  cat ~/.ssh/id_ed25519
  ```
- **Important**: Copy ENTIRE key including:
  - `-----BEGIN OPENSSH PRIVATE KEY-----`
  - All the key content
  - `-----END OPENSSH PRIVATE KEY-----`
- Status: ☐ Configured

### 4. VPS_PORT (Optional)
- **Description**: SSH port (defaults to 22)
- **Example**: `22`
- **Value**: `_____________________________________`
- Status: ☐ Configured (or skip to use default)

## Optional Secrets

These can be configured in `.env.production` on VPS instead:

### 5. OPENROUTER_API_KEY (Optional)
- **Description**: OpenRouter API key for AI models
- **Example**: `sk-or-v1-...`
- **Value**: `_____________________________________`
- Status: ☐ Configured in GitHub ☐ Configured in VPS .env.production

### 6. SITE_URL (Optional)
- **Description**: Production URL
- **Example**: `bookgen.yourdomain.com`
- **Value**: `_____________________________________`
- Status: ☐ Configured in GitHub ☐ Configured in VPS .env.production

### 7. SITE_TITLE (Optional)
- **Description**: Application title
- **Example**: `BookGen - AI Biography Generator`
- **Value**: `_____________________________________`
- Status: ☐ Configured in GitHub ☐ Configured in VPS .env.production

## Verification Checklist

After configuring secrets:

- ☐ All required secrets are added to GitHub
- ☐ VPS_SSH_KEY includes BEGIN and END lines
- ☐ SSH key is properly formatted (no extra spaces or line breaks)
- ☐ Public key is copied to VPS (`ssh-copy-id`)
- ☐ Can SSH to VPS manually: `ssh -i ~/.ssh/key user@host`
- ☐ VPS has Docker installed and running
- ☐ VPS user is in docker group
- ☐ /opt/bookgen directory exists and is writable
- ☐ docker-compose.prod.yml is on VPS

## Testing SSH Connection

Before pushing, test SSH connection manually:

```bash
# Test connection with your key
ssh -i ~/.ssh/your_key your_user@your_vps

# Should connect without password
# If successful, the GitHub Action will work
```

## Common Issues

### SSH Key Format Error
**Problem**: Key has extra spaces or missing BEGIN/END lines  
**Solution**: Copy entire key including headers, no modifications

### Permission Denied
**Problem**: Public key not on VPS  
**Solution**: Run `ssh-copy-id -i ~/.ssh/key.pub user@vps`

### User Not in Docker Group
**Problem**: Docker commands fail with permission error  
**Solution**: `sudo usermod -aG docker username` then logout/login

## Next Steps

1. ☐ Configure all required secrets above
2. ☐ Complete VPS preparation (see QUICK_START_CICD.md)
3. ☐ Test SSH connection manually
4. ☐ Push to main branch to trigger deployment
5. ☐ Monitor at: https://github.com/JPMarichal/bookgen/actions

---

**Documentation**: See `CI_CD_IMPLEMENTATION.md` for detailed setup guide.
