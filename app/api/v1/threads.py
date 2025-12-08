from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from jose import jwt

from app.db.session import get_db
from app.models.thread import Thread
from app.api.v1.auth import get_current_user
from app.schemas.thread import ThreadCreate, ThreadRead, ThreadList
from app.models.user import User
from app.models.vote import Vote
from app.schemas.auth import TokenPayload
from app.core.config import settings
from pydantic import BaseModel

# --- HELPERS ---

def is_admin(user: User) -> bool:
    return bool(
        getattr(user, "role", None) and getattr(user.role, "name", "") == "admin"
    )

def is_admin_or_mod(user: User) -> bool:
    if not user.role:
        return False
    return user.role.name in ["admin", "moderator"]

# 1. Helper to manually extract User ID from header (so Guests don't get 401 Error)
def get_user_id_from_header(authorization: Optional[str], db: Session):
    if not authorization:
        return None
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = TokenPayload(**payload)
        return token_data.sub
    except:
        return None

# 2. Helper to Calculate Score & Check if User Voted
def enrich_thread_with_votes(thread, db: Session, user_id: Optional[int] = None):
    # Calculate Score (Sum of all votes)
    score = db.query(func.sum(Vote.value)).filter(Vote.thread_id == thread.id).scalar()
    thread.score = score or 0

    # Check User Vote (1, -1, or 0)
    if user_id:
        user_vote = db.query(Vote.value).filter(
            Vote.thread_id == thread.id,
            Vote.user_id == user_id
        ).scalar()
        thread.user_vote = user_vote or 0
    else:
        thread.user_vote = 0
    
    return thread

router = APIRouter(prefix="/threads", tags=["threads"])

# --- ROUTES ---

@router.post("/", response_model=ThreadRead, status_code=status.HTTP_201_CREATED)
def create_thread(
    payload: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = Thread(
        title=payload.title,
        content=payload.content,
        owner_id=current_user.id,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    # New threads have 0 score, no enrichment needed strictly, but good practice
    thread.score = 0
    thread.user_vote = 0
    return thread


@router.get("/", response_model=ThreadList)
def list_threads(
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None) # <--- Manual Header Read
):
    # Identify the user (if logged in)
    current_user_id = get_user_id_from_header(authorization, db)

    if page < 1: page = 1
    if page_size < 1 or page_size > 100: page_size = 10

    query = db.query(Thread)

    if search:
        like = f"%{search}%"
        query = query.filter((Thread.title.ilike(like)) | (Thread.content.ilike(like)))
    total = query.count()

    threads = (
        query.order_by(Thread.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    # 3. ENRICH WITH VOTES
    for t in threads:
        enrich_thread_with_votes(t, db, current_user_id)

    # Convert to Pydantic models manually to ensure score/user_vote are included
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
    authorization: Optional[str] = Header(None) 
):
    current_user_id = get_user_id_from_header(authorization, db)

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

    # ENRICH WITH VOTES
    for t in threads:
        enrich_thread_with_votes(t, db, current_user_id)

    return ThreadList(
        items=[ThreadRead.model_validate(t, from_attributes=True) for t in threads],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{thread_id}", response_model=ThreadRead)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None) 
):
    current_user_id = get_user_id_from_header(authorization, db)

    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="thread not found"
        )
    
    # ENRICH WITH VOTES
    enrich_thread_with_votes(thread, db, current_user_id)

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

    if thread.owner_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not allowed to edit this thread")

    thread.title = payload.title
    thread.content = payload.content

    db.commit()
    db.refresh(thread)
    
    # Enrich before returning (User is current_user)
    enrich_thread_with_votes(thread, db, current_user.id)
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

    if thread.owner_id != current_user.id and not is_admin_or_mod(current_user):
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(thread)
    db.commit()
    return None


# --- VOTE LOGIC ---
class VoteRequest(BaseModel):
    dir: int # 1 or -1

@router.post("/{thread_id}/vote")
@router.post("/{thread_id}/vote")
def vote_thread(
    thread_id: int, 
    vote_req: VoteRequest,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 1. Check Thread
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # 2. Find Existing Vote
    found_vote = db.query(Vote).filter(
        Vote.thread_id == thread_id, 
        Vote.user_id == current_user.id
    ).first()

    dir = vote_req.dir # 1 (Up) or -1 (Down)

    if found_vote:
        if found_vote.value == dir:
            # User clicked same button -> REMOVE Vote (Toggle off)
            db.delete(found_vote)
        else:
            # User changed mind (Up -> Down or Down -> Up) -> UPDATE Vote
            found_vote.value = dir
    else:
        # No previous vote -> CREATE Vote
        new_vote = Vote(user_id=current_user.id, thread_id=thread_id, value=dir)
        db.add(new_vote)

    db.commit()

    # 3. Return the new total score
    new_score = db.query(func.sum(Vote.value)).filter(Vote.thread_id == thread_id).scalar() or 0
    
    return {"score": new_score}