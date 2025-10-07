# 📖 BookGen Documentation Map

This document helps you navigate between the structured documentation in `/docs` and the existing technical documentation in the repository root.

## 🗺️ Navigation Guide

### Start Here
- **Main Documentation**: [docs/](docs/) - Organized, user-friendly guides
- **Quick Reference**: [docs/INDEX.md](docs/INDEX.md) - Complete documentation index
- **Getting Started**: [docs/getting-started/](docs/getting-started/) - Installation and setup

---

## 📂 Documentation Structure

### User-Facing Documentation (`/docs`)

**Purpose**: Easy-to-navigate guides for all user types

```
docs/
├── INDEX.md                    # Complete navigation index
├── README.md                   # Documentation overview
├── getting-started/            # For new users
├── api/                        # For developers
├── user-guide/                 # For end users
├── architecture/               # For architects
├── operations/                 # For DevOps
└── emergency/                  # For on-call
```

### Technical Documentation (Root)

**Purpose**: Detailed implementation guides and reference material

Located in repository root for easy access during development.

---

## 🔗 Documentation Mapping

### Installation & Setup

| Topic | User Guide | Technical Reference |
|-------|------------|---------------------|
| **Installation** | [docs/getting-started/installation.md](docs/getting-started/installation.md) | [DEPLOYMENT.md](DEPLOYMENT.md) |
| **Configuration** | [docs/getting-started/configuration.md](docs/getting-started/configuration.md) | Various .md files |
| **Quick Start** | [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md) | Quick start guides |
| **VPS Setup** | [docs/operations/deployment.md](docs/operations/deployment.md) | [VPS_SETUP.md](VPS_SETUP.md) |
| **Docker** | [docs/operations/deployment.md](docs/operations/deployment.md) | [DOCKER_README.md](DOCKER_README.md) |

### API & Development

| Topic | User Guide | Technical Reference |
|-------|------------|---------------------|
| **API Overview** | [docs/api/overview.md](docs/api/overview.md) | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |
| **FastAPI** | [docs/api/overview.md](docs/api/overview.md) | [FASTAPI_IMPLEMENTATION_SUMMARY.md](FASTAPI_IMPLEMENTATION_SUMMARY.md) |
| **Architecture** | [docs/architecture/system-overview.md](docs/architecture/system-overview.md) | Various implementation docs |
| **Testing** | [docs/INDEX.md](docs/INDEX.md) | [TESTING_STRATEGY.md](TESTING_STRATEGY.md) |

### Core Features

| Feature | User Guide | Technical Reference |
|---------|------------|---------------------|
| **Biography Creation** | [docs/user-guide/creating-biographies.md](docs/user-guide/creating-biographies.md) | [ENGINE_QUICK_START.md](ENGINE_QUICK_START.md) |
| **Notifications** | [docs/user-guide/notifications.md](docs/user-guide/notifications.md) | [NOTIFICATION_SYSTEM.md](NOTIFICATION_SYSTEM.md) |
| **Source Validation** | [docs/user-guide/creating-biographies.md](docs/user-guide/creating-biographies.md) | [ADVANCED_SOURCE_VALIDATION.md](ADVANCED_SOURCE_VALIDATION.md) |
| **Length Validation** | In API docs | [LENGTH_VALIDATION_README.md](LENGTH_VALIDATION_README.md) |
| **Word Export** | In user guide | [WORD_EXPORT_QUICKSTART.md](WORD_EXPORT_QUICKSTART.md) |

### Operations

| Topic | User Guide | Technical Reference |
|-------|------------|---------------------|
| **Deployment** | [docs/operations/deployment.md](docs/operations/deployment.md) | [DEPLOYMENT.md](DEPLOYMENT.md), [VPS_SETUP.md](VPS_SETUP.md) |
| **Runbooks** | [docs/operations/runbooks.md](docs/operations/runbooks.md) | [VERIFICATION_COMMANDS.md](VERIFICATION_COMMANDS.md) |
| **Troubleshooting** | [docs/operations/troubleshooting.md](docs/operations/troubleshooting.md) | [VPS_SETUP.md](VPS_SETUP.md) |
| **CI/CD** | [docs/operations/deployment.md](docs/operations/deployment.md) | [CI_CD_IMPLEMENTATION.md](CI_CD_IMPLEMENTATION.md) |
| **Monitoring** | [docs/operations/runbooks.md](docs/operations/runbooks.md) | [IMPLEMENTATION_SUMMARY_ISSUE_15.md](IMPLEMENTATION_SUMMARY_ISSUE_15.md) |

---

## 📚 Technical Documentation Reference

### Quick Start Guides (Root)

Fast-track guides for specific components:

- [QUICKSTART_API.md](QUICKSTART_API.md) - API quick start
- [QUICKSTART_DATABASE.md](QUICKSTART_DATABASE.md) - Database setup
- [ENGINE_QUICK_START.md](ENGINE_QUICK_START.md) - State machine engine
- [QUICK_START_CICD.md](QUICK_START_CICD.md) - CI/CD setup
- [QUICK_START_LENGTH_VALIDATION.md](QUICK_START_LENGTH_VALIDATION.md) - Length validation
- [QUICK_START_SOURCE_VALIDATION.md](QUICK_START_SOURCE_VALIDATION.md) - Source validation
- [WORD_EXPORT_QUICKSTART.md](WORD_EXPORT_QUICKSTART.md) - Document export
- [NOTIFICATION_QUICKSTART.md](NOTIFICATION_QUICKSTART.md) - Notifications

### Component Documentation (Root)

Deep-dive technical documentation:

- [CELERY_TASK_QUEUE.md](CELERY_TASK_QUEUE.md) - Celery implementation
- [DATABASE_README.md](DATABASE_README.md) - Database design
- [DOCKER_README.md](DOCKER_README.md) - Docker configuration
- [DOCKER_OPTIMIZATION.md](DOCKER_OPTIMIZATION.md) - Docker best practices
- [NOTIFICATION_SYSTEM.md](NOTIFICATION_SYSTEM.md) - Notification architecture
- [OPENROUTER_INTEGRATION.md](OPENROUTER_INTEGRATION.md) - LLM integration
- [ADVANCED_SOURCE_VALIDATION.md](ADVANCED_SOURCE_VALIDATION.md) - Source validation
- [LENGTH_VALIDATION_README.md](LENGTH_VALIDATION_README.md) - Length validation
- [CONCATENATION_SERVICE_README.md](CONCATENATION_SERVICE_README.md) - Document concatenation

### Implementation Summaries (Root)

Track completed work and implementation details:

- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Overall summary
- [IMPLEMENTATION_DATABASE.md](IMPLEMENTATION_DATABASE.md) - Database implementation
- [FASTAPI_IMPLEMENTATION_SUMMARY.md](FASTAPI_IMPLEMENTATION_SUMMARY.md) - API implementation
- [IMPLEMENTATION_SUMMARY_ISSUE_7.md](IMPLEMENTATION_SUMMARY_ISSUE_7.md) - Length validation
- [IMPLEMENTATION_SUMMARY_ISSUE_8.md](IMPLEMENTATION_SUMMARY_ISSUE_8.md) - Source validation
- [IMPLEMENTATION_SUMMARY_ISSUE_9.md](IMPLEMENTATION_SUMMARY_ISSUE_9.md) - Notifications
- [IMPLEMENTATION_SUMMARY_ISSUE_10.md](IMPLEMENTATION_SUMMARY_ISSUE_10.md) - State machine
- [IMPLEMENTATION_SUMMARY_ISSUE_11.md](IMPLEMENTATION_SUMMARY_ISSUE_11.md) - Integration
- [IMPLEMENTATION_SUMMARY_ISSUE_12.md](IMPLEMENTATION_SUMMARY_ISSUE_12.md) - Docker
- [IMPLEMENTATION_SUMMARY_ISSUE_13.md](IMPLEMENTATION_SUMMARY_ISSUE_13.md) - CI/CD
- [IMPLEMENTATION_SUMMARY_ISSUE_14.md](IMPLEMENTATION_SUMMARY_ISSUE_14.md) - Testing
- [IMPLEMENTATION_SUMMARY_ISSUE_15.md](IMPLEMENTATION_SUMMARY_ISSUE_15.md) - Monitoring

### Deployment Documentation (Root)

Production deployment guides:

- [DEPLOYMENT.md](DEPLOYMENT.md) - General deployment guide
- [VPS_SETUP.md](VPS_SETUP.md) - VPS Ubuntu IONOS setup
- [CI_CD_IMPLEMENTATION.md](CI_CD_IMPLEMENTATION.md) - CI/CD pipeline
- [VERIFICATION_COMMANDS.md](VERIFICATION_COMMANDS.md) - Verification procedures

### Project Documentation (Root)

- [PLAN_TRABAJO.md](PLAN_TRABAJO.md) - Work plan (Spanish)
- [REQUERIMIENTOS_SISTEMA_AUTOMATIZADO.md](REQUERIMIENTOS_SISTEMA_AUTOMATIZADO.md) - System requirements

---

## 🎯 Which Documentation Should I Use?

### For New Users
→ **Start with `/docs`**
- Better organized
- User-friendly language
- Complete workflows
- Navigation aids

### For Developers
→ **Use both**
- `/docs` for overview and integration
- Root docs for implementation details
- Quick starts for specific components

### For DevOps
→ **Start with `/docs/operations`**
- Then reference root deployment docs
- Use quick starts for setup
- Keep runbooks handy

### For Contributors
→ **Use root documentation**
- Implementation summaries
- Technical deep-dives
- Component architecture
- Development guides

---

## 📖 Reading Paths by Goal

### Goal: Install and Run BookGen

```
1. docs/getting-started/installation.md
2. docs/getting-started/configuration.md
3. docs/getting-started/quick-start.md
```

### Goal: Develop API Integration

```
1. docs/api/overview.md
2. API_DOCUMENTATION.md (technical details)
3. FASTAPI_IMPLEMENTATION_SUMMARY.md (implementation)
4. Interactive docs at /docs endpoint
```

### Goal: Deploy to Production

```
1. docs/operations/deployment.md (overview)
2. VPS_SETUP.md (detailed VPS setup)
3. DEPLOYMENT.md (additional details)
4. docs/operations/runbooks.md (operations)
```

### Goal: Understand System Architecture

```
1. docs/architecture/system-overview.md (high-level)
2. IMPLEMENTATION_SUMMARY.md (overall)
3. Component-specific docs (detailed)
4. Implementation summaries (issues 7-15)
```

### Goal: Troubleshoot Issues

```
1. docs/operations/troubleshooting.md (common issues)
2. VPS_SETUP.md (deployment troubleshooting)
3. docs/emergency/incident-response.md (critical issues)
4. Component-specific docs (detailed debugging)
```

### Goal: Contribute to Project

```
1. README.md (project overview)
2. TESTING_STRATEGY.md (testing approach)
3. Implementation summaries (completed work)
4. Component documentation (architecture)
```

---

## 🔄 Documentation Maintenance

### `/docs` Directory
- **Purpose**: User-facing, organized guides
- **Updates**: With major releases
- **Format**: Markdown
- **Audience**: All users

### Root Documentation
- **Purpose**: Technical reference, implementation details
- **Updates**: During development
- **Format**: Markdown
- **Audience**: Developers, contributors

### Keeping in Sync
- User guides reference technical docs for details
- Technical docs link to user guides for context
- Changes in one should be reflected in the other
- Use this map to maintain consistency

---

## 📝 Contributing to Documentation

### User Documentation (`/docs`)
- Focus on clarity and user workflows
- Test all examples
- Include screenshots where helpful
- Keep navigation current

### Technical Documentation (Root)
- Focus on implementation details
- Document design decisions
- Include code examples
- Link to user guides

### Both
- Keep cross-references updated
- Maintain consistency
- Follow existing format
- Test all commands

---

## 🆘 Getting Help

### For Documentation Questions
- Check this map first
- Use [docs/INDEX.md](docs/INDEX.md) for navigation
- Search repository for keywords
- Open GitHub issue for missing docs

### For Technical Issues
- [docs/operations/troubleshooting.md](docs/operations/troubleshooting.md) - Common issues
- Component-specific docs - Detailed help
- [GitHub Issues](https://github.com/JPMarichal/bookgen/issues) - Report problems

### For Emergencies
- [docs/emergency/incident-response.md](docs/emergency/incident-response.md) - Critical procedures
- [VPS_SETUP.md](VPS_SETUP.md) - VPS troubleshooting

---

**Last Updated**: January 2025  
**Documentation Version**: 1.0.0

---

[Main Documentation](docs/) | [Complete Index](docs/INDEX.md) | [README](README.md)
