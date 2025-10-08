# Quick Reference - Database Models

## Setup Database

```python
# One-time setup - create database schema
from src.database.config import init_db
init_db()

# Or use Alembic migrations (recommended)
# alembic upgrade head
```

## Basic Usage

```python
from src.database.config import SessionLocal
from src.models import Biography, Chapter
from src.repositories import BiographyRepository, ChapterRepository

# Create session
db = SessionLocal()

# Use repositories
bio_repo = BiographyRepository(db)
chapter_repo = ChapterRepository(db)

# Create biography
bio = Biography(character_name="Albert Einstein", status="pending")
bio = bio_repo.create(bio)

# Create chapter
chapter = Chapter(
    biography_id=bio.id,
    number=1,
    title="Early Life",
    word_count=1500
)
chapter = chapter_repo.create(chapter)

# Clean up
db.close()
```

## FastAPI Integration

```python
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.repositories import BiographyRepository

router = APIRouter()

@router.get("/biographies/{bio_id}")
def get_biography(bio_id: int, db: Session = Depends(get_db)):
    repo = BiographyRepository(db)
    return repo.get_by_id(bio_id)

@router.post("/biographies")
def create_biography(character_name: str, db: Session = Depends(get_db)):
    repo = BiographyRepository(db)
    bio = Biography(character_name=character_name, status="pending")
    return repo.create(bio)
```

## Common Queries

```python
# Get biography with chapters
bio_with_chapters = bio_repo.get_with_chapters(bio_id)

# Get chapters by biography
chapters = chapter_repo.get_by_biography(bio_id)

# Get total word count
total_words = chapter_repo.get_total_word_count(bio_id)

# Get active jobs
active_jobs = job_repo.get_active_jobs()

# Get valid sources above threshold
good_sources = source_repo.get_by_relevance_threshold(0.8)
```

## Environment Configuration

```bash
# .env file
DATABASE_URL=sqlite:///./data/bookgen.db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DEBUG=false
```

## Migration Commands

```bash
# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Current version
alembic current
```

## Testing

```bash
# Run database tests
pytest tests/test_database.py -v

# Run verification
python scripts/verification/verify_database_implementation.py
```
