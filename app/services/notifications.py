from sqlalchemy.orm import Session
from app.models.notification import Notification
from typing import Optional

import anyio
from app.websocket.notifications_ws import manager

def create_notification(db:Session,user_id:int,message:str):
    notif=Notification(user_id=user_id,message=message)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    # Fire-and-forget push to WebSocket (if user connected)
    async def _push():
        await manager.send_personal_json(
            user_id,
            {
                "id": notif.id,
                "message": notif.message,
                "read": notif.read,
                "user_id": notif.user_id,
                "created_at": notif.created_at.isoformat(),
            },
        )

    try:
        # We are in a threadpool (sync endpoint), this bridges to the main event loop
        anyio.from_thread.run(_push)
    except RuntimeError:
        # No running loop (e.g. during tests) – just ignore WS push
        pass

    return notif
