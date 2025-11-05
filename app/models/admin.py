from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Admin(db.Model):
    __tablename__ = 'admins'

    id_admin: Mapped[int] = mapped_column(primary_key=True)
    nombre_admin: Mapped[str] = mapped_column(String(100), nullable=False)
    email_admin: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_admin: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __init__(self, nombre_admin: str, email_admin: str, password_admin: str):
        self.nombre_admin = nombre_admin
        self.email_admin = email_admin
        self.password_admin = generate_password_hash(password_admin)

    def set_password(self, password: str) -> None:
        self.password_admin = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_admin, password)
    
    def serialize(self) -> dict:
        return {
            'id_admin': self.id_admin,
            'nombre_admin': self.nombre_admin,
            'email_admin': self.email_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def serialize_public(self) -> dict:
        return {
            'id_admin': self.id_admin,
            'nombre_admin': self.nombre_admin,
            'email_admin': self.email_admin
        }
    
    def __repr__(self) -> str:
        return f'<Admin {self.nombre_admin} ({self.email_admin})>'