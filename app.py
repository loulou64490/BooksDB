import sqlite3
import ollama

from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def execute_query(query, params=(), fetchone=False, commit=False):
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
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


# TODO: ajouter de l'ia
# résumé commentaire
# TODO: affichage mobile
# TODO: suppression commentaire
# compte commentaire
@app.route('/')
def accueil():
    rate = execute_query(
        "SELECT books.id, title, author, year, AVG(rating) as average FROM books LEFT JOIN comments ON books.id=comments.book_id GROUP BY books.id ORDER BY average DESC LIMIT 5", )
    comment = execute_query(
        "SELECT books.id, title, author, year, COUNT(comment) as count FROM books LEFT JOIN comments ON books.id=comments.book_id GROUP BY books.id ORDER BY count DESC LIMIT 5", )
    recent = execute_query("SELECT * FROM books ORDER BY id DESC LIMIT 5", )
    last_comment = execute_query(
        "SELECT books.id, title, author, year, comment, rating FROM books LEFT JOIN comments ON books.id=comments.book_id ORDER BY comments.id DESC LIMIT 5", )
    return render_template('index.html', rate=rate, comment=comment, recent=recent, last_comment=last_comment)


@app.route('/livre')
def livre():
    book_id = request.args.get('id')
    data = execute_query("SELECT * FROM books WHERE id=?", [book_id], fetchone=True)
    if data:
        comments = execute_query("SELECT comment, rating FROM comments WHERE book_id=? ORDER BY id DESC", [book_id], )
        if comments:
            average = round(
                execute_query("SELECT AVG(rating) FROM comments WHERE book_id=?", [book_id], fetchone=True)[0], 1)
            return render_template('livre.html', data=data, comments=comments, average=average)
        else:
            return render_template('livre.html', data=data)
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
        if len(data) == 1:
            return redirect(f"/livre?id={data[0]['id']}", 303)
        else:
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


@app.route('/modifier', methods=['POST'])
def modifier():
    book_id = request.args.get('id')
    if 'delete' in request.form:
        handle_modification(book_id, delete=True)
        return redirect("/", 303)
    else:
        book_id = handle_modification(book_id)
        return redirect(f"/livre?id={book_id}", 303)


@app.route('/commenter', methods=['POST'])
def commenter():
    book_id = request.args.get('id')
    execute_query(
        "INSERT INTO comments (book_id, comment, rating) VALUES (?, ?, ?)",
        [book_id, request.form['comment'], request.form['rating']],
        commit=True
    )
    return redirect(f"/livre?id={book_id}", 303)


if __name__ == '__main__':
    app.run(debug=True)
