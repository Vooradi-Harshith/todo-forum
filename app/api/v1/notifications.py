from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.notification import NotificationRead, NotificationList
from app.models.notification import Notification
from app.api.v1.auth import get_current_user
from app.models.user import User

router=APIRouter(prefix="/notifications",tags=['notifications'])


@router.get('/',response_model=NotificationList)
def get_notifications(page:int=1,
                      page_size:int=10,
                      db:Session=Depends(get_db),
                      current_user:User=Depends(get_current_user)):
    q=db.query(Notification).filter(Notification.user_id==current_user.id)
    total=q.count()
    items=q.order_by(Notification.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return NotificationList(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )



# Mark notification as read
@router.put("/{id}/read", response_model=NotificationRead)
def mark_as_read(id: int, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):

    notif = db.query(Notification).filter(Notification.id == id,
                                          Notification.user_id == current_user.id).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.read = True
    db.commit()
    db.refresh(notif)
    return notif
@router.get("/unread", response_model=NotificationList)
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 10,
):
    q = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    )

    notifications = (
        q.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return NotificationList(
        items=[NotificationRead.model_validate(n, from_attributes=True) for n in notifications],
        total=q.count(),
        page=page,
        page_size=page_size
    )


# ===========================
# 2️⃣ MARK ONE AS READ
# ===========================
@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.read = True
    db.commit()
    db.refresh(notif)
    return notif


# ===========================
# 3️⃣ MARK ALL AS READ
# ===========================
@router.patch("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).update({Notification.read: True})

    db.commit()
    return {"status": "success", "message": "All notifications marked as read"}