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
├── guides/                     # How-to guides
├── architecture/               # For architects
├── operations/                 # For DevOps
├── emergency/                  # For on-call
├── technical/                  # Technical documentation
│   ├── quickstart/             # Quick start guides
│   ├── components/             # Component deep-dives
│   ├── deployment/             # Deployment guides
│   └── testing/                # Testing strategies
├── archive/                    # Historical implementation docs
└── project/                    # Project planning docs (Spanish)
```

### Technical Documentation (`/docs/technical`)

**Purpose**: Quick-reference technical guides and component documentation

Located in `/docs/technical/` for organized access:
- **Quick Start Guides** (`technical/quickstart/`): Component-specific getting started docs
- **Component Documentation** (`technical/components/`): Deep-dive technical references
- **Deployment Guides** (`technical/deployment/`): Production deployment specifics
- **Testing & Verification** (`technical/testing/`): Testing strategies and verification

---

## 🔗 Documentation Mapping

### Installation & Setup

| Topic | User Guide | Technical Reference |
|-------|------------|---------------------|
| **Installation** | [docs/getting-started/installation.md](docs/getting-started/installation.md) | [docs/technical/deployment/DEPLOYMENT.md](docs/technical/deployment/DEPLOYMENT.md) |
| **Configuration** | [docs/getting-started/configuration.md](docs/getting-started/configuration.md) | Various technical docs |
| **Quick Start** | [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md) | [docs/technical/quickstart/](docs/technical/quickstart/) |
| **VPS Setup** | [docs/operations/deployment.md](docs/operations/deployment.md) | [docs/technical/deployment/VPS_SETUP.md](docs/technical/deployment/VPS_SETUP.md) |
| **Docker** | [docs/operations/deployment.md](docs/operations/deployment.md) | [docs/technical/components/DOCKER_README.md](docs/technical/components/DOCKER_README.md) |

### API & Development

| Topic | User Guide | Technical Reference |
|-------|------------|---------------------|
| **API Overview** | [docs/api/overview.md](docs/api/overview.md) | [docs/technical/components/API_DOCUMENTATION.md](docs/technical/components/API_DOCUMENTATION.md) |
| **Architecture** | [docs/architecture/system-overview.md](docs/architecture/system-overview.md) | [docs/technical/components/](docs/technical/components/) |
| **Testing** | [docs/INDEX.md](docs/INDEX.md) | [docs/technical/testing/TESTING_STRATEGY.md](docs/technical/testing/TESTING_STRATEGY.md) |

### Core Features

| Feature | User Guide | Technical Reference |
|---------|------------|---------------------|
| **Biography Creation** | [docs/user-guide/creating-biographies.md](docs/user-guide/creating-biographies.md) | [docs/technical/quickstart/ENGINE_QUICK_START.md](docs/technical/quickstart/ENGINE_QUICK_START.md) |
| **Notifications** | [docs/user-guide/notifications.md](docs/user-guide/notifications.md) | [docs/technical/components/NOTIFICATION_SYSTEM.md](docs/technical/components/NOTIFICATION_SYSTEM.md) |
| **Source Validation** | [docs/user-guide/creating-biographies.md](docs/user-guide/creating-biographies.md) | [docs/technical/components/ADVANCED_SOURCE_VALIDATION.md](docs/technical/components/ADVANCED_SOURCE_VALIDATION.md) |
| **Length Validation** | In API docs | [docs/technical/components/LENGTH_VALIDATION_README.md](docs/technical/components/LENGTH_VALIDATION_README.md) |
| **Word Export** | In user guide | [docs/technical/quickstart/WORD_EXPORT_QUICKSTART.md](docs/technical/quickstart/WORD_EXPORT_QUICKSTART.md) |
| **Project Structure** | N/A | [docs/technical/components/DIRECTORY_MIGRATION.md](docs/technical/components/DIRECTORY_MIGRATION.md) |

### Operations

| Topic | User Guide | Technical Reference |
|-------|------------|---------------------|
| **Deployment** | [docs/operations/deployment.md](docs/operations/deployment.md) | [docs/technical/deployment/](docs/technical/deployment/) |
| **Runbooks** | [docs/operations/runbooks.md](docs/operations/runbooks.md) | [docs/technical/testing/VERIFICATION_COMMANDS.md](docs/technical/testing/VERIFICATION_COMMANDS.md) |
| **Troubleshooting** | [docs/operations/troubleshooting.md](docs/operations/troubleshooting.md) | [docs/technical/deployment/VPS_SETUP.md](docs/technical/deployment/VPS_SETUP.md) |
| **CI/CD** | [docs/operations/deployment.md](docs/operations/deployment.md) | [docs/technical/deployment/CI_CD_IMPLEMENTATION.md](docs/technical/deployment/CI_CD_IMPLEMENTATION.md) |

---

## 📚 Technical Documentation Reference

All technical documentation is now organized in [docs/technical/](docs/technical/).

### Quick Start Guides

Fast-track guides in [docs/technical/quickstart/](docs/technical/quickstart/):

- [QUICKSTART_API.md](docs/technical/quickstart/QUICKSTART_API.md) - API quick start
- [QUICKSTART_DATABASE.md](docs/technical/quickstart/QUICKSTART_DATABASE.md) - Database setup
- [ENGINE_QUICK_START.md](docs/technical/quickstart/ENGINE_QUICK_START.md) - State machine engine
- [QUICK_START_CICD.md](docs/technical/quickstart/QUICK_START_CICD.md) - CI/CD setup
- [QUICK_START_LENGTH_VALIDATION.md](docs/technical/quickstart/QUICK_START_LENGTH_VALIDATION.md) - Length validation
- [QUICK_START_SOURCE_VALIDATION.md](docs/technical/quickstart/QUICK_START_SOURCE_VALIDATION.md) - Source validation
- [QUICK_START_CONTENT_ANALYZER.md](docs/technical/quickstart/QUICK_START_CONTENT_ANALYZER.md) - Content analysis
- [QUICK_START_CROSS_VALIDATION.md](docs/technical/quickstart/QUICK_START_CROSS_VALIDATION.md) - Cross validation
- [QUICK_START_FEEDBACK_SYSTEM.md](docs/technical/quickstart/QUICK_START_FEEDBACK_SYSTEM.md) - Feedback system
- [QUICK_START_HYBRID_GENERATION.md](docs/technical/quickstart/QUICK_START_HYBRID_GENERATION.md) - Hybrid generation
- [QUICK_START_PERSONALIZED_STRATEGIES.md](docs/technical/quickstart/QUICK_START_PERSONALIZED_STRATEGIES.md) - Personalized strategies
- [QUICK_START_SOURCE_STRATEGIES.md](docs/technical/quickstart/QUICK_START_SOURCE_STRATEGIES.md) - Source strategies
- [WORD_EXPORT_QUICKSTART.md](docs/technical/quickstart/WORD_EXPORT_QUICKSTART.md) - Document export
- [NOTIFICATION_QUICKSTART.md](docs/technical/quickstart/NOTIFICATION_QUICKSTART.md) - Notifications

### Component Documentation

Deep-dive technical documentation in [docs/technical/components/](docs/technical/components/):

- [API_DOCUMENTATION.md](docs/technical/components/API_DOCUMENTATION.md) - Complete API reference
- [CELERY_TASK_QUEUE.md](docs/technical/components/CELERY_TASK_QUEUE.md) - Celery implementation
- [DATABASE_README.md](docs/technical/components/DATABASE_README.md) - Database design
- [DOCKER_README.md](docs/technical/components/DOCKER_README.md) - Docker configuration
- [DOCKER_OPTIMIZATION.md](docs/technical/components/DOCKER_OPTIMIZATION.md) - Docker best practices
- [NOTIFICATION_SYSTEM.md](docs/technical/components/NOTIFICATION_SYSTEM.md) - Notification architecture
- [OPENROUTER_INTEGRATION.md](docs/technical/components/OPENROUTER_INTEGRATION.md) - LLM integration
- [ADVANCED_SOURCE_VALIDATION.md](docs/technical/components/ADVANCED_SOURCE_VALIDATION.md) - Source validation
- [AUTOMATIC_SOURCE_GENERATION.md](docs/technical/components/AUTOMATIC_SOURCE_GENERATION.md) - Automatic source generation
- [CROSS_VALIDATION_IMPLEMENTATION.md](docs/technical/components/CROSS_VALIDATION_IMPLEMENTATION.md) - Cross validation
- [LENGTH_VALIDATION_README.md](docs/technical/components/LENGTH_VALIDATION_README.md) - Length validation
- [CONCATENATION_SERVICE_README.md](docs/technical/components/CONCATENATION_SERVICE_README.md) - Document concatenation
- [PERFORMANCE_OPTIMIZATION.md](docs/technical/components/PERFORMANCE_OPTIMIZATION.md) - Performance tuning

### Deployment Documentation

Production deployment guides in [docs/technical/deployment/](docs/technical/deployment/):

- [DEPLOYMENT.md](docs/technical/deployment/DEPLOYMENT.md) - IONOS VPS deployment (Spanish)
- [VPS_SETUP.md](docs/technical/deployment/VPS_SETUP.md) - VPS Ubuntu IONOS setup
- [CI_CD_IMPLEMENTATION.md](docs/technical/deployment/CI_CD_IMPLEMENTATION.md) - CI/CD pipeline

### Testing & Verification

Testing strategies in [docs/technical/testing/](docs/technical/testing/):

- [TESTING_STRATEGY.md](docs/technical/testing/TESTING_STRATEGY.md) - Testing approach
- [VERIFICATION_COMMANDS.md](docs/technical/testing/VERIFICATION_COMMANDS.md) - Verification procedures

### Historical Documentation (Archive)

Implementation summaries and historical records moved to [docs/archive/](docs/archive/):

- Implementation summaries from completed issues
- Historical completion reports
- Verification reports

See [docs/archive/README.md](docs/archive/README.md) for details.

### Project Planning Documentation

Planning documents and proposals moved to [docs/project/](docs/project/):

- Work plans (Spanish)
- System requirements (Spanish)
- Feature proposals (Spanish)

See [docs/project/README.md](docs/project/README.md) for details.

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
- `/docs/technical/` for implementation details
- Quick starts for specific components

### For DevOps
→ **Start with `/docs/operations`**
- Then reference `/docs/technical/deployment/`
- Use quick starts for setup
- Keep runbooks handy

### For Contributors
→ **Use `/docs/technical/` + archives**
- Component documentation for technical details
- Quick starts for component setup
- docs/archive/ for historical context
- docs/project/ for planning background

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
2. docs/technical/components/API_DOCUMENTATION.md (technical details)
3. Interactive docs at /docs endpoint
```

### Goal: Deploy to Production

```
1. docs/operations/deployment.md (overview)
2. docs/technical/deployment/VPS_SETUP.md (detailed VPS setup)
3. docs/technical/deployment/DEPLOYMENT.md (additional details)
4. docs/operations/runbooks.md (operations)
```

### Goal: Understand System Architecture

```
1. docs/architecture/system-overview.md (high-level)
2. docs/technical/components/ (detailed)
3. docs/archive/ (historical implementation details)
```

### Goal: Troubleshoot Issues

```
1. docs/operations/troubleshooting.md (common issues)
2. docs/technical/deployment/VPS_SETUP.md (deployment troubleshooting)
3. docs/emergency/incident-response.md (critical issues)
4. docs/technical/components/ (detailed debugging)
```

### Goal: Contribute to Project

```
1. README.md (project overview)
2. docs/technical/testing/TESTING_STRATEGY.md (testing approach)
3. docs/archive/ (historical implementations)
4. docs/technical/components/ (architecture)
```

---

## 🔄 Documentation Maintenance

### `/docs` Directory
- **Purpose**: User-facing, organized guides
- **Updates**: With major releases
- **Format**: Markdown
- **Audience**: All users

### `/docs/technical/` Directory
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

### Technical Documentation (`/docs/technical/`)
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
- [docs/technical/deployment/VPS_SETUP.md](docs/technical/deployment/VPS_SETUP.md) - VPS troubleshooting

---

**Last Updated**: January 2025  
**Documentation Version**: 2.0.0 (Root documentation fully consolidated)

**Recent Changes:**
- Moved all 32 technical documentation files from root to docs/technical/
- Organized into quickstart/, components/, deployment/, and testing/ subdirectories
- Updated all references and navigation
- **Cleaned root directory from 34 to 2 documentation files (README.md + DOCUMENTATION_MAP.md)**

---

[Main Documentation](docs/) | [Complete Index](docs/INDEX.md) | [README](README.md)
