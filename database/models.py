from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(20), nullable=False)