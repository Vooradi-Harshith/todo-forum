from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session


from app.db.session import get_db
from app.models.post import Post
from app.models.thread import Thread
from app.schemas.post import PostCreate, PostRead, PostList
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.notifications import create_notification
from app.models.notification import Notification

router=APIRouter(prefix='/threads',tags=['Posts'])


# app/api/v1/posts.py
def is_admin_or_mod(user: User) -> bool:
    if not user.role: return False
    return user.role.name in ["admin", "moderator"]

@router.post("/{thread_id}/posts", response_model=PostRead)
def create_post(thread_id: int, data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = Post(content=data.content, thread_id=thread_id, user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)

    # 🔔 Notify thread owner
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if thread and thread.owner_id != current_user.id:  # avoid self-notification
        db.add(Notification(
            user_id=thread.owner_id,
            message=f"{current_user.username} posted in your thread."
        ))
        db.commit()

    return post

@router.get("/{thread_id}/posts", response_model=PostList)
def list_posts(thread_id: int,
               page: int = 1,
               page_size: int = 10,
               db: Session = Depends(get_db)):

    query = db.query(Post).filter(Post.thread_id == thread_id)

    posts = (query.order_by(Post.created_at.asc())
                  .offset((page - 1) * page_size)
                  .limit(page_size)
                  .all())

    return PostList(
        items=[PostRead.model_validate(p) for p in posts],
        total=query.count(),
        page=page,
        page_size=page_size
    )


# ... existing imports ...
from fastapi import status # Make sure status is imported

@router.delete("/{thread_id}/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    thread_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Check permissions: Owner of the post OR Admin
    if post.user_id != current_user.id and not is_admin_or_mod(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    db.delete(post)
    db.commit()
    return None
