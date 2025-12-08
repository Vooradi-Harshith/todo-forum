from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    # Add ondelete="CASCADE" here 👇
    thread_id = Column(Integer, ForeignKey("threads.id", ondelete="CASCADE"), primary_key=True)
    value = Column(Integer, nullable=False) # 1 for upvote, -1 for downvote
