from sqlalchemy import Integer,String
from sqlalchemy.orm import mapped_column,Mapped,relationship
from app.db.base import Base
from app.models.base_model import BaseModel
class Role(Base,BaseModel):
    __tablename__="roles"

    name:Mapped[str]=mapped_column(String(50),unique=True)
    users:Mapped[list["User"]]=relationship(back_populates='role')