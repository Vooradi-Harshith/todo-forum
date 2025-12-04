# tests/factories.py

from app.models.user import User
from app.models.role import Role
from app.models.thread import Thread
from app.models.post import Post
from app.models.comment import Comment
from app.models.notification import Notification
from app.utils.security import hash_password


def create_role(db, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role
    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def create_user(db, username="user1", email=None, password="pass123") -> User:
    if email is None:
        email = f"{username}@example.com"

    member_role = create_role(db, "member")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role_id=member_role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_admin(db, username="admin", email=None, password="adminpass"):
    if email is None:
        email = f"{username}@example.com"

    admin_role = create_role(db, "admin")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role_id=admin_role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_thread(db, owner_id, title="Test Thread", content="Thread content") -> Thread:
    t = Thread(title=title, content=content, owner_id=owner_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def create_post(db, thread_id, user_id, content="Post content") -> Post:
    p = Post(content=content, thread_id=thread_id, user_id=user_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def create_comment(db, post_id, user_id, content="Comment", parent_id=None) -> Comment:
    c = Comment(content=content, post_id=post_id, user_id=user_id, parent_id=parent_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def create_notification(db, user_id, message="notification") -> Notification:
    n = Notification(user_id=user_id, message=message)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n
