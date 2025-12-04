from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from app.db.base import Base
from app.models.base_model import BaseModel


class Thread(Base, BaseModel):
    __tablename__ = "threads"

    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="threads")

    posts: Mapped[list["Post"]] = relationship(
        back_populates="thread", cascade="all, delete-orphan", passive_deletes=True
    )
