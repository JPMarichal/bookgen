# Database Models and Repositories

This module implements SQLAlchemy models and repository patterns for the BookGen system.

## Overview

The database layer consists of:
- **Models**: SQLAlchemy ORM models representing database entities
- **Repositories**: Data access layer with CRUD operations
- **Migrations**: Alembic-based database schema versioning

## Models

### Biography
Represents a biography generation project.

**Fields:**
- `id`: Primary key
- `character_name`: Name of the person/character (indexed)
- `status`: Generation status (pending, in_progress, completed, failed)
- `bio_metadata`: JSON field for additional metadata
- `created_at`, `updated_at`, `completed_at`: Timestamps
- `error_message`: Error tracking

**Relationships:**
- `chapters`: One-to-many with Chapter
- `generation_jobs`: One-to-many with GenerationJob

### Chapter
Represents a chapter in a biography.

**Fields:**
- `id`: Primary key
- `biography_id`: Foreign key to Biography
- `number`: Chapter number (unique per biography)
- `title`: Chapter title
- `content`: Chapter text content
- `word_count`: Number of words
- `created_at`, `updated_at`: Timestamps

### Source
Represents a research source for biography generation.

**Fields:**
- `id`: Primary key
- `url`: Source URL (indexed)
- `title`: Source title
- `author`: Source author
- `publication_date`: Publication date
- `relevance_score`: Relevance score (0.0-1.0)
- `validation_status`: Validation status (pending, valid, invalid, inaccessible)
- `source_type`: Type of source (url, book, article, document, other)
- `content_summary`: Summary of source content
- `created_at`, `updated_at`, `validated_at`: Timestamps

### GenerationJob
Represents a background generation job.

**Fields:**
- `id`: Primary key
- `biography_id`: Foreign key to Biography
- `status`: Job status (pending, running, completed, failed, paused)
- `progress`: Progress percentage (0.0-100.0)
- `current_phase`: Current processing phase
- `logs`: JSON logs
- `error_message`: Error tracking
- `job_metadata`: Additional metadata
- `created_at`, `updated_at`, `started_at`, `completed_at`: Timestamps

## Repositories

All repositories extend `BaseRepository` which provides:
- `create(obj)`: Create new record
- `get_by_id(id)`: Get by primary key
- `get_all(skip, limit)`: Get all with pagination
- `update(obj)`: Update existing record
- `delete(obj)`: Delete record
- `delete_by_id(id)`: Delete by ID
- `count()`: Count total records

### BiographyRepository
Additional methods:
- `get_by_character_name(name)`: Find by character name
- `get_by_status(status)`: Filter by status
- `get_with_chapters(id)`: Get with chapters eagerly loaded
- `get_recent(limit)`: Get most recent biographies

### ChapterRepository
Additional methods:
- `get_by_biography(biography_id)`: Get all chapters for a biography
- `get_by_biography_and_number(biography_id, number)`: Get specific chapter
- `count_by_biography(biography_id)`: Count chapters
- `get_total_word_count(biography_id)`: Total words across all chapters

### SourceRepository
Additional methods:
- `get_by_url(url)`: Find by URL
- `get_by_validation_status(status)`: Filter by validation status
- `get_by_relevance_threshold(min_relevance)`: Get sources above threshold
- `get_valid_sources()`: Get all valid sources
- `count_by_status(status)`: Count by validation status

### GenerationJobRepository
Additional methods:
- `get_by_biography(biography_id)`: Get all jobs for a biography
- `get_by_status(status)`: Filter by status
- `get_active_jobs()`: Get pending/running jobs
- `get_latest_by_biography(biography_id)`: Get most recent job
- `get_with_biography(id)`: Get with biography eagerly loaded

## Database Configuration

Configuration is managed through environment variables:

```bash
DATABASE_URL=sqlite:///./data/bookgen.db  # Default SQLite
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/bookgen

DB_POOL_SIZE=10          # Connection pool size (non-SQLite)
DB_MAX_OVERFLOW=20       # Max overflow connections
DEBUG=false              # Enable SQL query logging
```

### SQLite Configuration
- Uses `StaticPool` for connection pooling
- Foreign key constraints enabled
- Database stored in `./data/bookgen.db`

### PostgreSQL Configuration
- Configurable pool size and overflow
- Connection pre-ping enabled
- Recommended for production

## Migrations

Migrations are managed with Alembic.

### Common Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current migration
alembic current

# View migration history
alembic history
```

### Creating Migrations

1. Modify models in `src/models/`
2. Run: `alembic revision --autogenerate -m "Description"`
3. Review the generated migration in `alembic/versions/`
4. Apply: `alembic upgrade head`

## Usage Examples

### Using Models

```python
from src.database.config import SessionLocal
from src.models import Biography, Chapter

# Create session
db = SessionLocal()

# Create biography
biography = Biography(
    character_name="Albert Einstein",
    status="pending"
)
db.add(biography)
db.commit()
db.refresh(biography)

# Create chapter
chapter = Chapter(
    biography_id=biography.id,
    number=1,
    title="Early Life",
    content="Chapter content...",
    word_count=1500
)
db.add(chapter)
db.commit()

db.close()
```

### Using Repositories

```python
from src.database.config import SessionLocal
from src.models import Biography
from src.repositories import BiographyRepository

db = SessionLocal()
repo = BiographyRepository(db)

# Create
bio = Biography(character_name="Marie Curie", status="pending")
created = repo.create(bio)

# Read
found = repo.get_by_character_name("Marie Curie")

# Update
found.status = "completed"
updated = repo.update(found)

# Delete
repo.delete(updated)

db.close()
```

### Using with FastAPI Dependency Injection

```python
from fastapi import Depends
from src.database.config import get_db
from src.repositories import BiographyRepository

@app.get("/biographies/{bio_id}")
def get_biography(
    bio_id: int,
    db: Session = Depends(get_db)
):
    repo = BiographyRepository(db)
    biography = repo.get_by_id(bio_id)
    return biography
```

## Testing

Run the test suite:

```bash
# Run all database tests
pytest tests/test_database.py -v

# Run verification script
python verify_database_implementation.py
```

## Indexes

The following indexes are created for optimal query performance:

**Biographies:**
- `character_name` (individual)
- `status` (individual)
- `(status, created_at)` (composite)
- `(character_name, status)` (composite)

**Chapters:**
- `biography_id` (individual)
- `(biography_id, number)` (composite, unique)

**Sources:**
- `url` (individual)
- `validation_status` (individual)
- `created_at` (individual)
- `(validation_status, relevance_score)` (composite)

**GenerationJobs:**
- `biography_id` (individual)
- `status` (individual)
- `(status, created_at)` (composite)
- `(biography_id, status)` (composite)

## Best Practices

1. **Always use repositories** instead of direct model access
2. **Use context managers** or FastAPI dependencies for sessions
3. **Close sessions** after use to prevent connection leaks
4. **Use transactions** for multi-step operations
5. **Eager load relationships** when needed to avoid N+1 queries
6. **Review migrations** before applying to production
7. **Backup database** before running migrations in production

## Schema Diagram

```
Biography (1) ──< (N) Chapter
    │
    └──< (N) GenerationJob

Source (independent)
```

## Files Structure

```
src/
├── database/
│   ├── __init__.py       # Package exports
│   ├── base.py           # SQLAlchemy Base
│   └── config.py         # Database configuration & session management
├── models/
│   ├── __init__.py       # Model exports
│   ├── biography.py      # Biography model
│   ├── chapter.py        # Chapter model
│   ├── source.py         # Source model
│   └── generation_job.py # GenerationJob model
└── repositories/
    ├── __init__.py               # Repository exports
    ├── base.py                   # BaseRepository
    ├── biography_repository.py   # BiographyRepository
    ├── chapter_repository.py     # ChapterRepository
    ├── source_repository.py      # SourceRepository
    └── generation_job_repository.py # GenerationJobRepository

alembic/
├── versions/             # Migration files
├── env.py               # Alembic environment
├── script.py.mako       # Migration template
└── README               # Alembic README

alembic.ini              # Alembic configuration
```
