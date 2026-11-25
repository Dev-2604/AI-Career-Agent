
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator


class JobPreferenceCreate(BaseModel):
    target_role: str = Field(
        min_length=2,
        max_length=255,
    )

    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=150)

    remote_type: str | None = Field(default=None, max_length=50)
    employment_type: str | None = Field(default=None, max_length=50)
    experience_level: str | None = Field(default=None, max_length=100)

    min_salary: float | None = Field(default=None, ge=0)
    max_salary: float | None = Field(default=None, ge=0)

    salary_currency: str | None = Field(default=None, max_length=10)

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.min_salary is not None
            and self.max_salary is not None
            and self.min_salary > self.max_salary
        ):
            raise ValueError(
                "Minimum salary cannot exceed maximum salary."
            )

        return self


class JobPreferenceUpdate(BaseModel):
    target_role: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=150)

    remote_type: str | None = Field(default=None, max_length=50)
    employment_type: str | None = Field(default=None, max_length=50)
    experience_level: str | None = Field(default=None, max_length=100)

    min_salary: float | None = Field(default=None, ge=0)
    max_salary: float | None = Field(default=None, ge=0)

    salary_currency: str | None = Field(default=None, max_length=10)

    active: bool | None = None

    @model_validator(mode="after")
    def validate_salary_range(self):
        if (
            self.min_salary is not None
            and self.max_salary is not None
            and self.min_salary > self.max_salary
        ):
            raise ValueError(
                "Minimum salary cannot exceed maximum salary."
            )

        return self


class JobPreferenceResponse(BaseModel):
    id: UUID
    user_id: UUID

    target_role: str
    country: str | None = None
    city: str | None = None

    remote_type: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None

    min_salary: float | None = None
    max_salary: float | None = None
    salary_currency: str | None = None

    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
