from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    entity_id: UUID
    filename: str
    mime_type: str | None
    storage_path: str
    created_at: datetime

    model_config = {"from_attributes": True}
