# Midwest24 Archive — Database Schema

## Primary Tables

- users
- roles
- user_roles
- entities
- files
- metadata_fields
- metadata_values
- relationships
- versions
- activities
- ai_artifacts

## Conventions

- UUID primary keys
- snake_case names
- created_at / updated_at timestamps
- foreign key constraints
- soft delete where appropriate

## Search

Use PostgreSQL Full Text Search for MVP.

Future versions may introduce OpenSearch without changing the core schema.

## Object Storage

Files are stored outside PostgreSQL.

Database stores:

- storage_key
- checksum
- metadata
- relationships

Object storage stores binary content.
