# Midwest24 Core API Documentation Standards

**Document ID:** MW24-DEV-API-001  
**Version:** 1.0  
**Last Updated:** July 2026  
**Owner:** Jesse Russow  
**Applies To:** Midwest24 Core Development Repository

---

# Purpose

The `/tools/api/` directory serves as the operational documentation and API testing repository for every application that composes the Midwest24 Core platform.

These files are **developer documentation** and are **never deployed** to production websites.

They provide a single location for:

- API testing
- Health checks
- Authentication examples
- Operational commands
- Example requests
- Troubleshooting procedures
- Integration documentation

Rather than relying on external tools such as Postman or Insomnia, Midwest24 Core uses `.http` files directly within VSCodium using the REST Client extension.

---

# Philosophy

Documentation should be executable.

Every major service should have one location where an engineer can immediately discover:

- What the service does
- Where it lives
- How to authenticate
- How to verify health
- How to test APIs
- Common maintenance procedures
- Links to vendor documentation

The goal is that any qualified engineer can maintain the platform without searching through notes, emails, or external documentation.

---

# Directory Structure

```
tools/
└── api/
    ├── README.md
    ├── nextcloud.http
    ├── authentik.http
    ├── onlyoffice.http
    ├── odoo.http
    ├── immich.http
    ├── vaultwarden.http
    ├── cloudflare.http
    ├── github.http
    ├── google-workspace.http
    ├── plaid.http
    ├── nginx-proxy-manager.http
    └── truenas.http
```

---

# Naming Standard

The file name should always reflect the **actual application**, not the marketing name.

Correct:

```
nextcloud.http
```

Not:

```
midwest24-core-drive.http
```

Inside the file, document the branded product.

Example:

```http
###
# Midwest24 Core Drive
#
# Application:
# Nextcloud
#
# Purpose:
# Enterprise File Storage
# Document Collaboration
# Client Portal
#
```

This provides consistency for technical staff while preserving Midwest24 branding.

---

# Standard File Layout

Every `.http` file should follow the same structure.

```
Platform Information

Purpose

Documentation Links

Authentication

Health Checks

Common API Calls

Administrative Operations

Troubleshooting

Operational Notes

Related Services
```

---

# Example

```
###
# Midwest24 Core Drive
#
# Application:
# Nextcloud
#
# URL:
# https://drive.midwest24.com
#
# Purpose:
# Enterprise File Storage
# Document Synchronization
# Client Collaboration
#
```

---

# Authentication Section

Document:

- Login method
- OAuth
- API Keys
- Bearer Tokens
- Session Cookies
- WebAuthn
- Authentik integration

Never store secrets inside repository files.

Instead use variables.

Example:

```
Authorization: Bearer {{NEXTCLOUD_TOKEN}}
```

---

# Health Checks

Every application should have at least one health check.

Example:

```
GET https://drive.midwest24.com/status.php
```

Example:

```
GET https://auth.midwest24.com/api/v3/
```

---

# Common API Calls

Document the most frequently used requests.

Examples include:

- User lookup
- File upload
- Group management
- WebDAV requests
- Configuration retrieval
- Search
- Token validation

The objective is reducing repetitive documentation lookups.

---

# Administrative Operations

Include requests used during administration.

Examples:

- Create User
- Disable User
- Create Group
- Upload File
- Refresh Cache
- Start Scan
- Check Status

---

# Troubleshooting

Each file should contain operational procedures.

Examples:

```
Check service health

Restart service

Verify authentication

View logs

Verify API response

Common error codes

Known issues
```

---

# Related Documentation

Each API file should reference related manuals.

Example:

```
Midwest24 Core Operations Manual

Infrastructure Manual

Disaster Recovery

Security Standards

Identity Management

Application Deployment
```

---

# Version Control

These files are source code documentation.

Changes should be committed with Git alongside infrastructure changes.

Example:

```
git add tools/api/nextcloud.http

git commit -m "Document Nextcloud maintenance API"

git push
```

---

# Security Standards

Never commit:

- Passwords
- API Keys
- Private Keys
- Tokens
- Secrets
- Session Cookies

Use environment variables or REST Client variables.

---

# Required Applications

The following applications should maintain dedicated API documentation.

## Infrastructure

- TrueNAS
- Cloudflare
- Nginx Proxy Manager
- Authentik

## Productivity

- Nextcloud
- OnlyOffice
- Immich

## Business

- Odoo
- Plaid
- Stripe (future)

## Security

- Vaultwarden
- Authentik

## Development

- GitHub
- Google Workspace APIs

---

# Midwest24 Core Design Principle

Every application deployed within Midwest24 Core should have a corresponding `.http` documentation file.

This documentation becomes the operational reference for:

- Development
- Administration
- Disaster Recovery
- Automation
- API Testing
- Platform Expansion

No application should exist within the platform without accompanying operational documentation.

This standard ensures the Midwest24 Core platform remains maintainable, scalable, and transferable while reducing institutional knowledge loss and accelerating future development.
