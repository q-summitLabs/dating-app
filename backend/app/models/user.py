from sqlalchemy import ARRAY, JSON, Boolean, Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, SCHEMA_PREFIX, TimestampMixin, UUIDPrimaryKeyMixin

class User(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    interests = Column(ARRAY(String))
    location = Column(String)
    pictures = Column(ARRAY(String))
    prompts = Column(JSON)
    auth_user = relationship("AuthUser", back_populates="profile", uselist=False)


class AuthUser(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "auth_users"

    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_PREFIX}users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    last_login = Column(DateTime(timezone=True))
    profile = relationship("User", back_populates="auth_user", uselist=False)
