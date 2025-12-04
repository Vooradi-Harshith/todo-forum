from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from app.db.base import Base
from app.models.base_model import BaseModel


class Notification(Base, BaseModel):
    __tablename__ = "notifications"

    message: Mapped[str] = mapped_column(String(255))
    read: Mapped[bool] = mapped_column(default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Backref for easy join
    user = relationship("User", back_populates="notifications")
