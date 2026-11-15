from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    job_id: int
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = Field(
        default=None,
        max_length=50,
    )
    notes: str | None = None


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
