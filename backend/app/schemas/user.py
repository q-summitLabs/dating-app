from __future__ import annotations

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    interests: Optional[List[str]] = None
    location: Optional[str] = None
    pictures: Optional[List[str]] = None
    prompts: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

