from fastapi import FastAPI
from app.db import models
from app.api.v1 import auth

app=FastAPI(title='Discussion forum API')
app.include_router(auth.router)