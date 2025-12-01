from sqlalchemy.orm import mapped_column,Mapped,relationship
from sqlalchemy import Text,ForeignKey

from app.db.base import Base
from app.models.base_model import BaseModel


class Post(Base,BaseModel):
    __tablename__="posts"


    content:Mapped[str]=mapped_column(Text)
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("threads.id", ondelete="CASCADE")     # IMPORTANT 💥
    )
    thread:Mapped["Thread"]=relationship(back_populates="posts")

    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    user:Mapped["User"]=relationship(back_populates="posts")

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
