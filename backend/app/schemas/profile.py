
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class CandidateProfileUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    headline: str | None = Field(
        default=None,
        max_length=255,
    )

    summary: str | None = None

    skills: list[str] | None = None

    experience_level: str | None = Field(
        default=None,
        max_length=100,
    )

    total_experience_months: int | None = Field(
        default=None,
        ge=0,
    )

    education: list[dict] | None = None

    preferred_roles: list[str] | None = None


class CandidateProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    skills: list | None = None
    experience_level: str | None = None
    total_experience_months: int | None = None
    education: list | None = None
    preferred_roles: list | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
