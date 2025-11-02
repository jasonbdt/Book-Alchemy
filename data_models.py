from typing import Self

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Author(db.Model):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    birth_date: Mapped[DateTime] = mapped_column(DateTime)
    date_of_death: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    def __repr__(self: Self) -> str:
        return f"Author(id = {self.id}, " \
               f"name = {self.name})"


class Book(db.Model):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    publication_year: Mapped[DateTime] = mapped_column(DateTime)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    def __repr__(self: Self) -> str:
        return f"Book(id = {self.id}, " \
               f"title = {self.title})"
