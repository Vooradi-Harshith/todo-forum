from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentRead, CommentCreate, CommentList, CommentTree
from app.api.v1.auth import get_current_user
from app.services.notifications import create_notification
from app.core.permissions import is_admin,is_admin_or_mod


router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.post("/", response_model=CommentRead)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # If it's a reply to another comment
    parent_comment = None
    if payload.parent_id:
        parent_comment = (
            db.query(Comment).filter(Comment.id == payload.parent_id).first()
        )
        if not parent_comment:
            raise HTTPException(status_code=400, detail="Parent comment does not exist")

    new_comment = Comment(
        content=payload.content,
        post_id=post_id,
        user_id=current_user.id,
        parent_id=payload.parent_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # ===========================
    # 🔔 NOTIFICATIONS GENERATED
    # ===========================

    # Notify post owner (if not self)
    if post.user_id != current_user.id:
        create_notification(
            db, post.user_id, message=f"{current_user.username} commented on your post."
        )

    # Notify parent comment owner (only for nested reply)
    if (
        payload.parent_id
        and parent_comment
        and parent_comment.user_id != current_user.id
    ):
        create_notification(
            db,
            parent_comment.user_id,
            message=f"{current_user.username} replied to your comment.",
        )

    return new_comment


@router.get("/", response_model=CommentList)
def list_comments(
    post_id: int,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(Comment).filter(Comment.post_id == post_id)

    comments = (
        query.order_by(Comment.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return CommentList(
        items=[CommentRead.model_validate(c, from_attributes=True) for c in comments],
        total=query.count(),
        page=page,
        page_size=page_size,
    )


@router.get("/tree", response_model=list[CommentTree])
def list_comment_tree(post_id: int, db: Session = Depends(get_db)):

    comments = db.query(Comment).filter(Comment.post_id == post_id).all()

    # Convert comment rows → CommentTree models
    comment_map: dict[int, CommentTree] = {
        c.id: CommentTree.model_validate(c, from_attributes=True) for c in comments
    }

    # Ensure empty children array exists for each
    for obj in comment_map.values():
        obj.children = []

    roots: list[CommentTree] = []

    for c in comments:
        node = comment_map[c.id]
        if c.parent_id:
            comment_map[c.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


@router.put("/{comment_id}", response_model=CommentRead)
def update_comment(
    post_id: int,
    comment_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Only comment owner or admin can edit
    if comment.user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not allowed to edit this comment")

    comment.content = payload.content
    # Optional: allow re-parenting (or skip this line if you don't want that)
    comment.parent_id = payload.parent_id

    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Only comment owner or admin
    if comment.user_id != current_user.id and not is_admin_or_mod(current_user):
        raise HTTPException(
            status_code=403, detail="Not allowed to delete this comment"
        )

    db.delete(comment)
    db.commit()
    return None
