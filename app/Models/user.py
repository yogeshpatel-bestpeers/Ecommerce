import uuid
from enum import Enum

from app.database import Base
from sqlalchemy import String, Enum as sqlEnum
from sqlalchemy.orm import Mapped, mapped_column


class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    SELLER = "seller"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    passwords: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")

    role: Mapped[UserRole] = mapped_column(
        sqlEnum(UserRole, name="userrole"),
        nullable=False,
        default=UserRole.CUSTOMER,
    )
