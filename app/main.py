from fastapi import FastAPI, Depends
from app.db import models
from app.api.v1 import auth, threads, posts, comments, notifications
from app.websocket.notifications_ws import router as ws_notifications_router
from app.api.v1 import admin
from app.core.auth_roles import required_admin
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import SessionLocal,engine
from app.db.base import Base


from app.models.role import Role # <--- Import Role Model

# 1. DEFINE THE SEEDING FUNCTION
def create_default_roles():
    db = SessionLocal()
    try:
        roles = ["member", "moderator", "admin"]
        for role_name in roles:
            # Check if role exists
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                print(f"Creating role: {role_name}")
                new_role = Role(name=role_name)
                db.add(new_role)
        db.commit()
    except Exception as e:
        print(f"Error seeding roles: {e}")
    finally:
        db.close()
Base.metadata.create_all(bind=engine)

# 2. CALL IT ON STARTUP
create_default_roles()

app = FastAPI(title="Discussion forum API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(threads.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(notifications.router)
app.include_router(ws_notifications_router)
from app.core.auth_roles import required_admin

app.include_router(
    admin.router, dependencies=[Depends(required_admin)]  # 🔥 global admin lock
)
