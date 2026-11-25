
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    is_default: bool
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
