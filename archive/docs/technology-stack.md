# Midwest24 Archive — Technology Stack

## MVP Stack

- Backend: FastAPI
- Language: Python 3.12
- Database: PostgreSQL
- ORM: SQLAlchemy 2.0
- Migrations: Alembic
- Authentication: Authentik OIDC
- Frontend: React + Vite + TypeScript
- UI: Tailwind CSS + shadcn/ui
- API State: TanStack Query
- Storage: S3-compatible object storage
- MVP Search: PostgreSQL full-text search
- Future Search: OpenSearch
- Deployment: Docker Compose
- Testing: Pytest + Vitest

## MVP Rule

Do not introduce Kubernetes, GraphQL, OpenSearch, complex workflow engines, multi-tenant billing, ERP integration, CRM integration, or AI agents during the MVP unless explicitly approved.

The MVP should authenticate, upload, classify, search, retrieve, audit, backup, and restore.
