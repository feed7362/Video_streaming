import uuid

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTableUUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    __tablename__ = "oauth_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
