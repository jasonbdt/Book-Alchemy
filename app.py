import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import lazyload

from data_models import db, Author, Book

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


@app.route('/', methods=['GET'])
def home():
    sort_by = request.args.get('sort_by', 'book_title')
    print(request.args)
    if sort_by == 'book_title':
        print("BOOK TITLE")
        sort_key = Book.title
    elif sort_by == 'author_name':
        print("AUTHOR NAME")
        sort_key = Author.name

    sort_direction = request.args.get('direction', 'asc')
    if sort_direction == 'asc':
        print("ASC")
        sort_key = sort_key.asc()
    elif sort_direction == 'desc':
        print("DESC")
        sort_key = sort_key.desc()


    books = db.session.execute(
        db.select(Book).select_from(Author).join(Author.books).order_by(sort_key)
    ).scalars()

    return render_template("home.html", books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        author_name = request.form.get('name')
        birth_date = request.form.get('birthdate')
        date_of_death = request.form.get('date_of_death')

        author = Author(
            name=author_name,
            birth_date=datetime.strptime(birth_date, '%Y-%m-%d'),
            date_of_death=datetime.strptime(date_of_death, '%Y-%m-%d') if date_of_death else None
        )
        db.session.add(author)
        db.session.commit()
        return render_template("add_author.html", author=author)

    return render_template("add_author.html")


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = db.session.execute(
        db.select(Author)
    ).scalars()

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        book = Book(
            title=title,
            isbn=isbn,
            publication_year=datetime.strptime(publication_year, '%Y-%m-%d'),
            author_id=author_id
        )
        db.session.add(book)
        db.session.commit()
        return render_template("add_book.html", authors=authors, book=book)

    return render_template("add_book.html", authors=authors)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

# with app.app_context():
#     db.create_all()
