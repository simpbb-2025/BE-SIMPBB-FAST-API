from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, String, func

from app.core.database import Base


class User(Base):
    __tablename__ = "ipbb_user"

    id = Column(String(32), primary_key=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nama = Column(String(255), nullable=True)
    telepon = Column(String(255), nullable=False, server_default="")
    alamat = Column(String(255), nullable=False, server_default="")
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
    is_verified = Column(Boolean, nullable=False, default=False, server_default="0")
    hashed_password = Column("password", String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    is_admin = Column(Boolean, nullable=False, default=False, server_default="0")
