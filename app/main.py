from fastapi import FastAPI
from app.db import models
from app.api.v1 import auth
from app.api.v1 import threads
from app.api.v1 import posts
app=FastAPI(title='Discussion forum API')
app.include_router(auth.router)
app.include_router(threads.router)
app.include_router(posts.router)