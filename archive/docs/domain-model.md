# Midwest24 Archive — Domain Model

## Design Philosophy

Archive organizes organizational knowledge through entities and relationships.

Files support entities.
Metadata describes entities.
Relationships connect entities.

## Core Entity

Every object in Archive is an Entity.

Minimum fields:

- id (UUID)
- entity_type
- title
- description
- status
- created_at
- updated_at
- created_by
- owner_id

## Supporting Objects

### File

Stores immutable file references.

Fields:

- id
- entity_id
- filename
- mime_type
- storage_key
- checksum_sha256
- size_bytes

### Metadata

Typed metadata attached to entities.

Examples:

- category
- tag
- department
- project
- customer
- property
- priority

### Relationship

Defines directional relationships between entities.

Fields:

- source_entity_id
- relationship_type
- target_entity_id

### Version

Tracks changes over time.

### Activity

Append-only audit history.

### AI Artifact

Stores OCR, summaries, extracted entities, and future embeddings separately from authoritative data.
