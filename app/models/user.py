from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey
from app.db.base import Base
from app.models.base_model import BaseModel


class User(Base, BaseModel):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=2)
    role: Mapped["Role"] = relationship(back_populates="users")

    threads: Mapped[list["Thread"]] = relationship(back_populates="owner")
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    notifications: Mapped["Notification"] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
