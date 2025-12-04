from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models.thread import Thread
from app.api.v1.auth import get_current_user
from app.schemas.thread import ThreadCreate, ThreadRead, ThreadList
from app.models.user import User

def is_admin(user: User) -> bool:
    return bool(getattr(user, "role", None) and getattr(user.role, "name", "") == "admin")
def is_admin_or_mod(user: User) -> bool:
    if not user.role: return False
    return user.role.name in ["admin", "moderator"]

router=APIRouter(prefix='/threads',tags=['threads'])


@router.post('/',response_model=ThreadRead,status_code=status.HTTP_201_CREATED)
def create_thread(
    payload:ThreadCreate,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user),
):
    thread=Thread(
        title=payload.title,
        content=payload.content,
        owner_id=current_user.id,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread

@router.get('/',response_model=ThreadList)
def list_threads(
    page:int=1,
    page_size:int=10,
    search:str |None=None,
    db:Session=Depends(get_db)
):
    if page<1:
        page=1
    if page_size<1 or page_size>100:
        page_size=10

    query=db.query(Thread)

    if search:
        like=f'%{search}%'
        query=query.filter(
            (Thread.title.ilike(like)) |(Thread.content.ilike(like))
        )
    total=query.count()

    threads = (
        query
        .order_by(Thread.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    thread_items = [ThreadRead.model_validate(t, from_attributes=True) for t in threads]

    return ThreadList(
        items=thread_items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/search", response_model=ThreadList)
def search_threads(
    q: str,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(Thread).filter(
        or_(
            Thread.title.ilike(f"%{q}%"),
            Thread.content.ilike(f"%{q}%"),
        )
    )

    total = query.count()
    threads = (
        query.order_by(Thread.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ThreadList(
        items=[ThreadRead.model_validate(t, from_attributes=True) for t in threads],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get('/{thread_id}',response_model=ThreadRead)
def get_thread(
        thread_id:int,
        db:Session=Depends(get_db),
):
    thread=db.query(Thread).filter(Thread.id==thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='thread not found'
        )
    return thread

@router.put("/{thread_id}", response_model=ThreadRead)
def update_thread(
    thread_id: int,
    payload: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Only owner or admin
    if thread.owner_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not allowed to edit this thread")

    thread.title = payload.title
    thread.content = payload.content

    db.commit()
    db.refresh(thread)
    return thread

@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Only owner or admin
    if thread.owner_id != current_user.id and not is_admin_or_mod(current_user):
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(thread)
    db.commit()
    # 204 → empty body
    return None
