import uuid
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

Reason = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]


class MatchResult(BaseModel):
    issue_id: uuid.UUID
    match_pct: int = Field(ge=0, le=100)
    reasons: list[Reason] = Field(min_length=3, max_length=3)
