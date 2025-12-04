from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey, Integer
from app.db.base import Base
from app.models.base_model import BaseModel


class Comment(Base, BaseModel):
    __tablename__ = "comments"

    content: Mapped[str] = mapped_column(Text)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    post: Mapped["Post"] = relationship(back_populates="comments")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="comments")

    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("comments.id"), nullable=True
    )
    replies: Mapped[list["Comment"]] = relationship(
        back_populates="parent", cascade="all, delete"
    )
    parent: Mapped["Comment | None"] = relationship(
        back_populates="replies", remote_side="Comment.id"
    )
