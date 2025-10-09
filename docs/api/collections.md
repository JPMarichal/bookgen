# Collection-Based Automated Biography Generation

## Overview

The collections feature enables automated biography generation from collection files. Instead of manually specifying each character, you can maintain collection files (Markdown lists) and the system will automatically detect and generate biographies for the next uncompleted character.

## Collection File Format

Collection files are Markdown files stored in the `colecciones/` directory. They contain lists of characters with completion marks:

```markdown
1. Joseph Stalin ✅
2. Harry S. Truman ✅
3. Winston Churchill ✅
4. Dwight D. Eisenhower
5. Nikita Khrushchev
6. John F. Kennedy
```

- Characters with ✅ are considered completed
- Characters without ✅ are pending
- Numbering is optional but recommended for organization

## API Endpoints

### 1. Generate Next Biography from Collection

**Endpoint:** `POST /api/v1/collections/generate-next`

Automatically detects the first uncompleted character in a collection and starts biography generation.

**Request Body:**
```json
{
  "collection_file": "personajes_guerra_fria.md",
  "mode": "automatic",
  "chapters": 20,
  "total_words": 51000,
  "min_sources": 40,
  "quality_threshold": 0.8,
  "mark_completed": true,
  "sources": []
}
```

**Parameters:**
- `collection_file` (string, default: "personajes_guerra_fria.md"): Collection file name
- `mode` (string, default: "automatic"): Generation mode - "automatic", "manual", or "hybrid"
- `chapters` (integer, default: 20): Number of chapters to generate
- `total_words` (integer, default: 51000): Target word count
- `sources` (array, optional): Source URLs for manual/hybrid mode
- `min_sources` (integer, default: 40): Minimum sources for automatic/hybrid mode
- `quality_threshold` (float, default: 0.8): Quality threshold (0-1)
- `mark_completed` (boolean, default: true): Whether to mark character as completed in collection file

**Response (202 Accepted):**
```json
{
  "job_id": "d5bbc07e-5399-4346-b113-0d29775da133",
  "character": "Dwight D. Eisenhower",
  "character_normalized": "dwight_d_eisenhower",
  "collection_file": "personajes_guerra_fria.md",
  "line_number": "4.",
  "status": "pending",
  "mode": "automatic",
  "chapters": 20,
  "created_at": "2025-10-09T21:02:07.112586Z",
  "estimated_completion_time": "600 seconds",
  "message": "Biography generation started for 'Dwight D. Eisenhower' from collection 'personajes_guerra_fria.md'"
}
```

**Error Responses:**
- 404: Collection file not found or no uncompleted characters
- 400: Invalid request parameters
- 500: Internal server error

### 2. Get Collection Statistics

**Endpoint:** `GET /api/v1/collections/{collection_file}/stats`

Get statistics about a collection file.

**Response (200 OK):**
```json
{
  "collection_file": "personajes_guerra_fria.md",
  "total_characters": 100,
  "completed": 4,
  "remaining": 96,
  "completion_percentage": 4.0
}
```

### 3. List All Collections

**Endpoint:** `GET /api/v1/collections/`

Get a list of all available collection files.

**Response (200 OK):**
```json
{
  "collections": [
    "personajes_guerra_fria.md"
  ],
  "count": 1
}
```

## Usage Examples

### Example 1: Automated Generation

Generate the next biography using automatic source generation:

```bash
curl -X POST http://localhost:8000/api/v1/collections/generate-next \
  -H "Content-Type: application/json" \
  -d '{
    "collection_file": "personajes_guerra_fria.md",
    "mode": "automatic",
    "mark_completed": true
  }'
```

### Example 2: Manual Mode with Custom Sources

Generate biography with manually provided sources:

```bash
curl -X POST http://localhost:8000/api/v1/collections/generate-next \
  -H "Content-Type: application/json" \
  -d '{
    "collection_file": "personajes_guerra_fria.md",
    "mode": "manual",
    "chapters": 15,
    "mark_completed": true,
    "sources": [
      "https://example.com/source1",
      "https://example.com/source2",
      "https://example.com/source3",
      "https://example.com/source4",
      "https://example.com/source5",
      "https://example.com/source6",
      "https://example.com/source7",
      "https://example.com/source8",
      "https://example.com/source9",
      "https://example.com/source10"
    ]
  }'
```

### Example 3: Check Collection Progress

```bash
curl http://localhost:8000/api/v1/collections/personajes_guerra_fria.md/stats
```

### Example 4: Monitor Job Status

After starting generation, monitor the job using the standard biography status endpoint:

```bash
curl http://localhost:8000/api/v1/biographies/{job_id}/status
```

## Workflow Integration

The collections endpoint integrates seamlessly with existing infrastructure:

1. **Detection**: Finds the first uncompleted character in the collection
2. **Character Normalization**: Normalizes the character name for use as an identifier
3. **Biography Generation**: Calls the existing `/api/v1/biographies/generate` endpoint
4. **Marking**: Optionally marks the character as completed (✅) in the collection file
5. **Monitoring**: Job can be monitored via standard biography status endpoint

## Benefits

- **Automation**: No need to manually specify each character
- **Progress Tracking**: Visual progress in collection files with ✅ marks
- **Batch Processing**: Easy to process entire collections sequentially
- **Integration**: Reuses all existing biography generation infrastructure
- **Flexibility**: Supports all generation modes (automatic/manual/hybrid)

## Technical Notes

### Character Name Normalization

Character names are normalized for use as identifiers:
- Converted to lowercase
- Spaces replaced with underscores
- Special characters removed
- Example: "Dwight D. Eisenhower" → "dwight_d_eisenhower"

### Completion Marking

When `mark_completed: true`:
- The character is marked with ✅ in the collection file
- Marking happens after job creation, even if generation fails
- This prevents the same character from being picked again

### Error Handling

- Missing collection files return 404
- No uncompleted characters return 404 with descriptive message
- Source generation failures return 400 with error details
- Internal errors return 500 with error information

## Related Endpoints

- `POST /api/v1/biographies/generate` - Manual biography generation
- `GET /api/v1/biographies/{job_id}/status` - Job status monitoring
- `GET /api/v1/biographies/{job_id}/download` - Download completed biography
