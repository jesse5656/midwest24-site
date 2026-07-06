# Midwest24 Archive — REST API

## Base URL

/api/v1

## Resources

GET    /entities
POST   /entities
GET    /entities/{id}
PATCH  /entities/{id}
DELETE /entities/{id}

GET    /files/{id}
POST   /files

GET    /search

GET    /categories
GET    /tags

GET    /health

## Authentication

OIDC via Authentik.

JWT Bearer tokens.

## Authorization

Role Based Access Control.

Roles:

- Administrator
- Manager
- Contributor
- Viewer

## Response Format

All responses use JSON.

Errors follow RFC 9457 Problem Details where practical.
