from sqlalchemy.orm import DeclarativeBase

# 1. Define Base FIRST
class Base(DeclarativeBase):
    pass

# # 2. Import models AFTER Base is defined
# from app.models.user import User
# from app.models.role import Role
# from app.models.thread import Thread
# from app.models.post import Post
# from app.models.comment import Comment
# from app.models.notification import Notification
