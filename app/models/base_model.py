from datetime import datetime,timezone
from sqlalchemy import Integer,String
from sqlalchemy.orm import mapped_column,Mapped


class BaseModel:
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    created_at:Mapped[datetime]=mapped_column(default=datetime.now(timezone.utc))
    updated_at:Mapped[datetime]=mapped_column(default=datetime.now(timezone.utc),onupdate=datetime.now(timezone.utc))



