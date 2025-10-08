# Quick Start Guide - CI/CD Pipeline Setup

## 🚀 3-Minute Setup

### Step 1: Configure GitHub Secrets (2 minutes)

1. Go to: `https://github.com/JPMarichal/bookgen/settings/secrets/actions`
2. Click "New repository secret"
3. Add these secrets:

```
VPS_HOST = your-vps.ionos.com
VPS_USER = bookgen
VPS_SSH_KEY = (paste entire private key, including BEGIN and END lines)
```

### Step 2: Prepare VPS (1 minute)

SSH to your VPS and run:

```bash
# Quick setup script
sudo apt update && sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo useradd -m bookgen && sudo usermod -aG docker bookgen
sudo mkdir -p /opt/bookgen && sudo chown -R bookgen:bookgen /opt/bookgen
sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp
```

### Step 3: Deploy

Merge this PR or push to main:

```bash
git push origin main
```

Watch deployment at: `https://github.com/JPMarichal/bookgen/actions`

## ✅ Verify Deployment

```bash
# Check health
curl -f http://your-vps-ip:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2024-10-07T01:23:45","environment":"production","debug":false}
```

## 📚 Full Documentation

- **Complete Guide**: `CI_CD_IMPLEMENTATION.md`
- **Workflow Details**: `.github/workflows/README.md`
- **Testing Guide**: `tests/README.md`

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| SSH fails | Check VPS_HOST, VPS_USER, VPS_SSH_KEY are correct |
| Health check fails | SSH to VPS, run: `docker ps` and check logs |
| Tests fail | Run locally: `pytest tests/` |
| Image not found | Check GITHUB_TOKEN permissions in workflow |

## 🎯 What Was Implemented

✅ **Automated Testing** - Runs on every PR  
✅ **Docker Build** - Pushes to GitHub Container Registry  
✅ **Auto Deploy** - Deploys to VPS on main branch  
✅ **Health Checks** - Verifies deployment success  
✅ **Auto Rollback** - Reverts if deployment fails  
✅ **Notifications** - Reports workflow status  

---

**Need Help?** See `CI_CD_IMPLEMENTATION.md` for detailed instructions.
