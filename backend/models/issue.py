import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func

from backend.db.base import Base


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (
        UniqueConstraint("repo_full_name", "number", name="uq_issues_repo_number"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_full_name = Column(String(511), nullable=False, index=True)
    number = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=True)
    url = Column(String(1024), nullable=True)
    labels = Column(ARRAY(String), nullable=False, default=list)
    files_affected = Column(ARRAY(String), nullable=False, default=list)

    difficulty = Column(Float, nullable=False)
    difficulty_factors = Column(JSONB, nullable=False, default=dict)
    estimated_hours = Column(Float, nullable=True)

    scored_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
