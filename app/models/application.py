import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, func, ForeignKey, Enum as SqEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import ApplicationStatus

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    scheme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(SqEnum(ApplicationStatus), default=ApplicationStatus.DRAFT, index=True)
    data: Mapped[dict] = mapped_column(JSONB, default={}, server_default='{}')
    receipt_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # implicitly needed properly though not strictly asked, good practice

    # Relationships
    user: Mapped["User"] = relationship(back_populates="applications")
