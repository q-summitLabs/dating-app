from uuid import uuid4

from sqlalchemy import ARRAY, JSON, Boolean, Column, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "yolk_staging"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        default=uuid4,
    )
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    interests = Column(ARRAY(String))
    location = Column(String)
    pictures = Column(ARRAY(String))
    prompts = Column(JSON)
    auth_user = relationship("AuthUser", back_populates="profile", uselist=False)


class AuthUser(Base):
    __tablename__ = "auth_users"
    __table_args__ = {"schema": "yolk_staging"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        default=uuid4,
    )
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("yolk_staging.users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    profile = relationship("User", back_populates="auth_user", uselist=False)
