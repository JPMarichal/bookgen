# 📚 BookGen Documentation Index

Complete navigation guide for BookGen documentation.

## 🎯 Quick Links

### For New Users
- 👉 **[README](../README.md)** - Start here!
- ⚡ **[Quick Start](getting-started/quick-start.md)** - Get running in 5 minutes
- 📖 **[Installation Guide](getting-started/installation.md)** - Complete setup

### For Developers
- 🔌 **[API Overview](api/overview.md)** - REST API introduction
- 🏗️ **[Architecture](architecture/system-overview.md)** - System design
- 🧪 **[Testing Guide](../TESTING_STRATEGY.md)** - Testing infrastructure

### For Operations
- 🚀 **[Deployment](operations/deployment.md)** - Production deployment
- 📋 **[Runbooks](operations/runbooks.md)** - Operational procedures
- 🔧 **[Troubleshooting](operations/troubleshooting.md)** - Common issues

### For Emergencies
- 🚨 **[Incident Response](emergency/incident-response.md)** - Emergency procedures
- 🔥 **[Critical Issues](#critical-issues)** - Quick fixes

---

## 📖 Complete Documentation

### Getting Started

| Document | Description | Audience |
|----------|-------------|----------|
| [Installation](getting-started/installation.md) | Complete installation guide | All users |
| [Configuration](getting-started/configuration.md) | Environment setup and options | All users |
| [Quick Start](getting-started/quick-start.md) | Create your first biography | New users |

**Topics Covered:**
- Docker installation
- Manual installation
- Environment configuration
- Post-installation setup
- Verification steps

---

### API Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [API Overview](api/overview.md) | REST API introduction | Developers |

**Topics Covered:**
- Endpoint summary
- Authentication
- Request/response formats
- Error handling
- Rate limiting
- Integration examples

**Interactive Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### User Guides

| Document | Description | Audience |
|----------|-------------|----------|
| [Creating Biographies](user-guide/creating-biographies.md) | Step-by-step guide | End users |
| [Notifications](user-guide/notifications.md) | Understanding updates | End users, Developers |

**Topics Covered:**
- Source preparation
- Biography creation workflow
- Progress monitoring
- WebSocket integration
- Webhook implementation
- Email notifications
- Best practices

---

### Architecture & Design

| Document | Description | Audience |
|----------|-------------|----------|
| [System Overview](architecture/system-overview.md) | High-level architecture | Developers, Architects |

**Topics Covered:**
- Component architecture
- Data flow
- Security design
- Scalability
- Technology stack
- Performance characteristics

---

### Operations & Maintenance

| Document | Description | Audience |
|----------|-------------|----------|
| [Deployment](operations/deployment.md) | Production deployment | DevOps, Admins |
| [Runbooks](operations/runbooks.md) | Operational procedures | DevOps, Admins |
| [Troubleshooting](operations/troubleshooting.md) | Issue resolution | DevOps, Admins |

**Topics Covered:**
- VPS deployment
- Cloud deployment
- Service management
- Backup & restore
- Performance tuning
- Security operations
- Common issues
- Diagnostic commands

---

### Emergency Procedures

| Document | Description | Audience |
|----------|-------------|----------|
| [Incident Response](emergency/incident-response.md) | Critical incidents | DevOps, Admins |

**Topics Covered:**
- System down procedures
- Database corruption
- Security breach
- Worker crashes
- Disk space issues
- Memory exhaustion
- Post-incident procedures

---

## 🔍 Documentation by Topic

### Installation & Setup

1. **[Installation Guide](getting-started/installation.md)**
   - Docker installation
   - Manual installation
   - Prerequisites
   - Verification

2. **[Configuration](getting-started/configuration.md)**
   - Environment variables
   - Database setup
   - Redis configuration
   - Security settings

3. **[Deployment](operations/deployment.md)**
   - VPS deployment
   - Cloud platforms
   - Docker deployment
   - Post-deployment

### Using BookGen

1. **[Quick Start](getting-started/quick-start.md)**
   - First biography
   - Basic workflow
   - Monitoring progress

2. **[Creating Biographies](user-guide/creating-biographies.md)**
   - Source preparation
   - Validation
   - Submission
   - Monitoring
   - Retrieval

3. **[Notifications](user-guide/notifications.md)**
   - WebSocket
   - Webhooks
   - Email
   - Message types

### Development

1. **[API Overview](api/overview.md)**
   - Endpoints
   - Authentication
   - Examples
   - Error handling

2. **[Architecture](architecture/system-overview.md)**
   - System design
   - Components
   - Data flow
   - Scalability

3. **[Testing Strategy](../TESTING_STRATEGY.md)**
   - Test infrastructure
   - Running tests
   - Coverage goals

### Operations

1. **[Runbooks](operations/runbooks.md)**
   - Service management
   - Deployment procedures
   - Backup & restore
   - Performance tuning

2. **[Troubleshooting](operations/troubleshooting.md)**
   - Common issues
   - Diagnostic commands
   - Solutions

3. **[Monitoring](operations/runbooks.md#monitoring-and-alerts)**
   - Health checks
   - Log monitoring
   - Alerts

### Emergency

1. **[Incident Response](emergency/incident-response.md)**
   - Critical procedures
   - Recovery steps
   - Escalation paths
   - Post-incident review

---

## 🎓 Learning Paths

### Path 1: Complete Beginner

```
1. README.md
   ↓
2. Installation Guide
   ↓
3. Quick Start
   ↓
4. Creating Biographies
   ↓
5. Notifications Guide
```

**Estimated Time:** 2-3 hours

### Path 2: Developer Integration

```
1. README.md
   ↓
2. API Overview
   ↓
3. Architecture Overview
   ↓
4. Notifications Guide
   ↓
5. Testing Strategy
```

**Estimated Time:** 3-4 hours

### Path 3: Operations/DevOps

```
1. Installation Guide
   ↓
2. Configuration Guide
   ↓
3. Deployment Guide
   ↓
4. Runbooks
   ↓
5. Troubleshooting
   ↓
6. Incident Response
```

**Estimated Time:** 4-6 hours

---

## 📂 Additional Resources

### Implementation Guides

Located in root directory:

- **[Celery Task Queue](../CELERY_TASK_QUEUE.md)** - Task queue implementation
- **[Database](../DATABASE_README.md)** - Database setup and migrations
- **[Docker](../DOCKER_README.md)** - Docker configuration
- **[Engine Quick Start](../ENGINE_QUICK_START.md)** - State machine engine
- **[FastAPI Implementation](../FASTAPI_IMPLEMENTATION_SUMMARY.md)** - API summary
- **[Length Validation](../LENGTH_VALIDATION_README.md)** - Content validation
- **[Notification System](../NOTIFICATION_SYSTEM.md)** - Notifications deep dive
- **[OpenRouter Integration](../OPENROUTER_INTEGRATION.md)** - LLM integration
- **[Source Validation](../ADVANCED_SOURCE_VALIDATION.md)** - Source validation
- **[Word Export](../WORD_EXPORT_QUICKSTART.md)** - Document export

### Deployment Resources

- **[VPS Setup](../VPS_SETUP.md)** - Detailed VPS configuration
- **[CI/CD](../CI_CD_IMPLEMENTATION.md)** - Continuous deployment
- **[Docker Optimization](../DOCKER_OPTIMIZATION.md)** - Docker best practices

### Quick Start Guides

- **[API Quick Start](../QUICKSTART_API.md)**
- **[Database Quick Start](../QUICKSTART_DATABASE.md)**
- **[CI/CD Quick Start](../QUICK_START_CICD.md)**
- **[Length Validation Quick Start](../QUICK_START_LENGTH_VALIDATION.md)**
- **[Source Validation Quick Start](../QUICK_START_SOURCE_VALIDATION.md)**

### Implementation Summaries

Track completed work:

- [Issue #7: Length Validation](../IMPLEMENTATION_SUMMARY_ISSUE_7.md)
- [Issue #8: Advanced Source Validation](../IMPLEMENTATION_SUMMARY_ISSUE_8.md)
- [Issue #9: Notification System](../IMPLEMENTATION_SUMMARY_ISSUE_9.md)
- [Issue #10: State Machine](../IMPLEMENTATION_SUMMARY_ISSUE_10.md)
- [Issue #11: Integration](../IMPLEMENTATION_SUMMARY_ISSUE_11.md)
- [Issue #12: Docker](../IMPLEMENTATION_SUMMARY_ISSUE_12.md)
- [Issue #13: CI/CD](../IMPLEMENTATION_SUMMARY_ISSUE_13.md)
- [Issue #14: Testing](../IMPLEMENTATION_SUMMARY_ISSUE_14.md)
- [Issue #15: Monitoring](../IMPLEMENTATION_SUMMARY_ISSUE_15.md)

---

## 🔧 Critical Issues

Quick reference for common critical issues:

### System Down
1. Check all services: `docker-compose ps`
2. Restart: `docker-compose restart`
3. See: [Incident Response](emergency/incident-response.md#critical-complete-system-down)

### API Not Responding
1. Check logs: `docker logs bookgen-api`
2. Restart API: `docker-compose restart api`
3. See: [Troubleshooting](operations/troubleshooting.md#issue-api-not-responding)

### Worker Not Processing
1. Check worker: `docker logs bookgen-worker`
2. Check Redis: `docker exec bookgen-redis redis-cli ping`
3. See: [Troubleshooting](operations/troubleshooting.md#issue-worker-not-processing-jobs)

### Database Issues
1. Check DB: `docker logs bookgen-db`
2. Test connection: `docker exec bookgen-db pg_isready`
3. See: [Troubleshooting](operations/troubleshooting.md#issue-database-connection-failed)

---

## 📞 Getting Help

### Documentation Issues
- 🐛 [Report Documentation Bug](https://github.com/JPMarichal/bookgen/issues/new?labels=documentation)
- 💡 [Suggest Improvement](https://github.com/JPMarichal/bookgen/issues/new?labels=documentation,enhancement)

### Technical Support
- 📧 Email: support@bookgen.ai
- 💬 [GitHub Discussions](https://github.com/JPMarichal/bookgen/discussions)
- 🐛 [GitHub Issues](https://github.com/JPMarichal/bookgen/issues)

### Emergency Support
- 🚨 See [Incident Response](emergency/incident-response.md)
- 📞 Contact: [Emergency contacts in incident response doc]

---

## 📝 Documentation Standards

### Structure
- Each document has clear purpose
- Table of contents for long documents
- Navigation links (previous/next)
- Code examples are tested
- Commands are copy-pasteable

### Conventions
- ✅ = Completed/working
- ❌ = Not recommended/broken
- ⚠️ = Warning/caution
- 💡 = Tip/best practice
- 🔧 = Configuration/setup
- 📊 = Metrics/data
- 🚀 = Deployment/production

### Document Types
- **Guide**: Step-by-step instructions
- **Reference**: Comprehensive details
- **Overview**: High-level introduction
- **Runbook**: Operational procedures
- **Troubleshooting**: Problem solving

---

## 🔄 Documentation Updates

This documentation is actively maintained. Last major update: January 2025

**Contributing:**
- Documentation follows same PR process as code
- Test all commands before documenting
- Keep examples up-to-date
- Use consistent formatting

**Version Compatibility:**
- Documentation matches version 1.0.0
- Breaking changes noted in each document
- Migration guides provided when needed

---

[← Back to README](../README.md)
