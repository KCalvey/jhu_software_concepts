import os
from typing import Optional
from datetime import date

from sqlalchemy import create_engine, Integer, Text, Float, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass

class Applicant(Base):
    __tablename__ = "applicants"

    p_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    program: Mapped[Optional[str]] = mapped_column(Text)
    comments: Mapped[Optional[str]] = mapped_column(Text)
    date_added: Mapped[Optional[date]] = mapped_column(Date)
    url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(Text)
    term: Mapped[Optional[str]] = mapped_column(Text)
    us_or_international: Mapped[Optional[str]] = mapped_column(Text)

    gpa: Mapped[Optional[float]] = mapped_column(Float)
    gre: Mapped[Optional[float]] = mapped_column(Float)
    gre_v: Mapped[Optional[float]] = mapped_column(Float)
    gre_aw: Mapped[Optional[float]] = mapped_column(Float)

    degree: Mapped[Optional[str]] = mapped_column(Text)
    llm_generated_program: Mapped[Optional[str]] = mapped_column(Text)
    llm_generated_university: Mapped[Optional[str]] = mapped_column(Text)

DB_NAME = os.getenv("DB_NAME", "module3_db")
DB_USER = os.getenv("DB_USER", "karicalvey")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)