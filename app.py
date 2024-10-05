import sqlite3
# import ollama  # TODO: ajouter de l'ia
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(query, params=(), fetchone=False, commit=False):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        if commit:
            conn.commit()
            return cur
        if fetchone:
            result = cur.fetchone()
        else:
            result = cur.fetchall()
    finally:
        cur.close()
        conn.close()
    return result


# TODO: page d'accueil
@app.route('/')
def accueil():
    return render_template('index.html')


@app.route('/livre')
def livre():
    book_id = request.args.get('id')
    if book_id:
        data = execute_query("SELECT * FROM books WHERE id=?", [book_id], fetchone=True)
        if data:
            comments = execute_query("SELECT comment, rating FROM comments WHERE book_id=?", [book_id], )
            if comments:
                average = execute_query("SELECT AVG(rating) FROM comments WHERE book_id=?", [book_id], fetchone=True)
                return render_template('livre.html', data=data, comments=comments, average=average)
            else:
                return render_template('livre.html', data=data)
        else:
            return redirect("/recherche", 303)
    else:
        return redirect("/recherche", 303)


@app.route('/recherche', methods=['POST', 'GET'])
def recherche():
    if request.method == 'POST' and request.form['query']:
        query = request.form['query']
        search_params = ['%' + query + '%'] * 3
        data = execute_query(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ?",
            search_params
        )
        return render_template('recherche.html', data=data, result=query)
    return render_template('recherche.html')


def handle_modification(book_id=None, delete=False):
    if delete:
        execute_query("DELETE FROM books WHERE id=?", [book_id], commit=True)
    elif book_id:
        execute_query(
            "UPDATE books SET title=?, author=?, year=? WHERE id=?",
            [request.form['title'], request.form['author'], request.form['year'], book_id],
            commit=True
        )
    else:
        cur = execute_query(
            "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
            [request.form['title'], request.form['author'], request.form['year']],
            commit=True
        )
        book_id = cur.lastrowid
    return book_id


@app.route('/modifier', methods=['POST', 'GET'])
def modifier():
    book_id = request.args.get('id')

    if request.method == 'POST':
        if 'delete' in request.form:
            handle_modification(book_id, delete=True)
            return redirect("/", 303)
        else:
            book_id = handle_modification(book_id)
            return redirect(f"/livre?id={book_id}", 303)

    if book_id:
        data = execute_query("SELECT title, author, year FROM books WHERE id=?", [book_id], fetchone=True)
        return render_template('modifier.html', data=data, id=book_id)
    return render_template('modifier.html')


if __name__ == '__main__':
    app.run(debug=True)
