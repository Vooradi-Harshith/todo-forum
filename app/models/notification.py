from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey
from app.db.base import Base
from app.models.base_model import BaseModel

class Notification(Base, BaseModel):
    __tablename__ = "notifications"

    message: Mapped[str] = mapped_column(String(255))
    read: Mapped[bool] = mapped_column(default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
