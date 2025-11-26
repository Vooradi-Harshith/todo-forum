from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.thread import Thread
from app.api.v1.auth import get_current_user
from app.schemas.thread import ThreadCreate, ThreadRead, ThreadList
from app.models.user import User

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
