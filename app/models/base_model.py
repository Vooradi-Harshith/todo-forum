from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

class BaseModel:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc),              # python default
        server_default=func.now()                        # DB default 🔥
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        server_default=func.now()
    )
