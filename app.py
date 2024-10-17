import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

# import ollama
# import flask_login

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vous-ne-trouverez-jamais'


def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    with sqlite3.connect('books.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)

        if commit:
            conn.commit()
            return cur

        if fetchone:
            return cur.fetchone()

        if fetchall:
            return cur.fetchall()
        return None


# TODO: formulaire avec flask-wtf
# TODO: connexion avec flask-login
# TODO: ajouter de l'ia
# résumé commentaire
# TODO: affichage mobile
# TODO: recherche avancée
# dernière recherche
# TODO: améliorer page d'accueil
# dernier commentaire : afficher
# TODO: réécrire CSS
@app.route('/')
def accueil():
    data = {
        'rate': execute_query(
            "SELECT books.id, title, author, year, AVG(rating) as average "
            "FROM books LEFT JOIN comments ON books.id=comments.book_id "
            "GROUP BY books.id ORDER BY average DESC LIMIT 5", fetchall=True),
        'comment': execute_query(
            "SELECT books.id, title, author, year, COUNT(comment) as count "
            "FROM books LEFT JOIN comments ON books.id=comments.book_id "
            "GROUP BY books.id ORDER BY count DESC LIMIT 5", fetchall=True),
        'recent': execute_query("SELECT * FROM books ORDER BY id DESC LIMIT 5", fetchall=True),
        'last_comment': execute_query(
            "SELECT books.id, title, author, year, comment, rating "
            "FROM books LEFT JOIN comments ON books.id=comments.book_id "
            "ORDER BY comments.id DESC LIMIT 5", fetchall=True)
    }
    return render_template('index.html', data=data)


@app.route('/livre')
def livre():
    book_id = request.args.get('id')
    data = execute_query("SELECT * FROM books WHERE id=?", [book_id], fetchone=True)
    if data:
        comments = execute_query("SELECT * FROM comments WHERE book_id=? ORDER BY id DESC", [book_id], fetchall=True)
        if comments:
            average = round(
                execute_query("SELECT AVG(rating) FROM comments WHERE book_id=?", [book_id], fetchone=True)[0], 1)
            if average.is_integer():
                average = int(average)
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
            search_params, fetchall=True
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


def modify_comment(action, comment_id, book_id, form_data=None):
    if action == 'delete':
        execute_query("DELETE FROM comments WHERE id=?", [comment_id], commit=True)
    elif action == 'signal':
        execute_query("UPDATE comments SET signal=signal+1 WHERE id=?", [comment_id], commit=True)
        signal = execute_query("SELECT signal FROM comments WHERE id=?", [comment_id], fetchone=True)[0]
        if signal > 5:
            execute_query("DELETE FROM comments WHERE id=?", [comment_id], commit=True)
    elif action == 'modify' and form_data:
        execute_query("UPDATE comments SET comment=?, rating=? WHERE id=?",
                      [form_data['comment'], form_data['rating'], comment_id], commit=True)


@app.route('/commenter', methods=['POST'])
def commenter():
    book_id = request.args.get('id')
    if 'delete' in request.form:
        modify_comment('delete', request.form['delete'], book_id)
    elif 'signal' in request.form:
        modify_comment('signal', request.form['signal'], book_id)
    elif 'modify' in request.form:
        modify_comment('modify', request.form['modify'], book_id, request.form)
    else:
        execute_query(
            "INSERT INTO comments (book_id, comment, rating) VALUES (?, ?, ?)",
            [book_id, request.form['comment'], request.form['rating']],
            commit=True
        )
    return redirect(f"/livre?id={book_id}", 303)


if __name__ == '__main__':
    app.run(debug=True)
