from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session,joinedload

from app.db.session import get_db
from app.models.user import User
from app.models.thread import Thread
from app.models.post import Post
from app.models.comment import Comment
from app.core.auth_roles import required_admin
from app.models.role import Role
from app.schemas.user import UserRead
router=APIRouter(prefix='/admin',tags=['admin'])


# ============================ USER MANAGEMENT ============================

@router.get("/users")
def list_users(db: Session = Depends(get_db), admin=Depends(required_admin)):
    return db.query(User).options(joinedload(User.role)).all()


@router.put("/users/{user_id}/promote")
def promote_user(user_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")

    admin_role = db.query(Role).filter(Role.name == "admin").first()
    user.role_id = admin_role.id
    db.commit()
    return {"message": f"{user.username} promoted to admin"}


@router.put("/users/{user_id}/promote_mod")
def promote_to_moderator(user_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")

    # Find or Create 'moderator' role
    role = db.query(Role).filter(Role.name == "moderator").first()
    if not role:
        role = Role(name="moderator")
        db.add(role); db.commit(); db.refresh(role)
    
    user.role_id = role.id
    db.commit()
    return {"message": f"{user.username} is now a Moderator"}




@router.put("/users/{user_id}/demote")
def demote_user(user_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Correct role name = "member"
    user_role = db.query(Role).filter(Role.name == "member").first()
    if not user_role:
        # If DB doesn't have the role, create it
        user_role = Role(name="member")
        db.add(user_role)
        db.commit()
        db.refresh(user_role)

    user.role_id = user_role.id
    db.commit()
    return {"message": f"{user.username} demoted to member"}

# ============================ THREAD CONTROL ============================

@router.delete("/threads/{thread_id}")
def delete_thread_admin(thread_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread: raise HTTPException(404, "Thread not found")

    db.delete(thread); db.commit()
    return {"message": "Thread deleted by admin"}


# ============================ POSTS & COMMENTS ============================

@router.delete("/posts/{post_id}")
def delete_post_admin(post_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post: raise HTTPException(404, "Post not found")

    db.delete(post); db.commit()
    return {"message": "Post deleted by admin"}


@router.delete("/comments/{comment_id}")
def delete_comment_admin(comment_id: int, db: Session = Depends(get_db), admin=Depends(required_admin)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment: raise HTTPException(404, "Comment not found")

    db.delete(comment); db.commit()
    return {"message": "Comment deleted by admin"}