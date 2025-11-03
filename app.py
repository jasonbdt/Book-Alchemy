import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_

from data_models import db, Author, Book

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = "ThisIsAVeryVerySecretKey"
db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    sort_by = request.args.get('sort_by', 'book_title')
    if sort_by == 'book_title':
        sort_key = Book.title
    elif sort_by == 'author_name':
        sort_key = Author.name

    sort_direction = request.args.get('direction', 'asc')
    if sort_direction == 'asc':
        sort_key = sort_key.asc()
    elif sort_direction == 'desc':
        sort_key = sort_key.desc()

    search_query = request.form.get('search_query')
    if search_query:
        books = db.session.execute(
            db.select(Book).select_from(Author).join(Author.books)
            .filter(or_(
                Book.title.like(f"%{search_query}%"),
                Book.isbn.like(f"%{search_query}%"),
                Author.name.like(f"%{search_query}%"),
            )).order_by(sort_key)
        ).scalars()
    else:
        books = db.session.execute(
            db.select(Book).select_from(Author).join(Author.books)
            .order_by(sort_key)
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
        flash(f"Author \"{author.name}\" has been created successfully.", "system")
        db.session.commit()
        return redirect(url_for("add_author"))

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
        flash(f"New Book \"{book.title}\" created successfully.", "system")
        db.session.commit()

        return redirect(url_for('add_book'))

    return render_template("add_book.html", authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id: int):
    book = db.one_or_404(
        db.select(Book).filter(Book.id == book_id)
    )
    db.session.delete(book)
    flash(f"Book with ID {book.id} has been deleted successfully.", "system")

    if not book.author.books:
        author = db.one_or_404(
            db.select(Author).filter(Author.id == book.author.id)
        )
        db.session.delete(author)
        flash(f"Author with ID {author.id} has been deleted successfully.", "system")

    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

# with app.app_context():
#     db.create_all()
