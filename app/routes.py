from app import app
from flask import render_template, request, redirect
from app.models import execute_query, handle_modification, modify_comment


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


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
    query = request.form['query']
    if request.method == 'POST' and request.form['query']:
        search_params = ['%' + query + '%'] * 3
        data = execute_query(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ?",
            search_params, fetchall=True
        )
        if len(data) == 1:
            return redirect(f"/livre?id={data[0]['id']}", 303)
    else:
        data = execute_query("SELECT * FROM books", fetchall=True)
    return render_template('recherche.html', data=data, result=query)


@app.route('/modifier', methods=['POST'])
def modifier():
    book_id = request.args.get('id')
    if 'delete' in request.form:
        handle_modification(request.form, book_id, delete=True)
        return redirect("/", 303)
    else:
        book_id = handle_modification(request.form, book_id)
        return redirect(f"/livre?id={book_id}", 303)


@app.route('/commenter', methods=['POST'])
def commenter():
    book_id = request.args.get('id')
    if 'delete' in request.form:
        modify_comment('delete', request.form['delete'])
    elif 'signal' in request.form:
        modify_comment('signal', request.form['signal'])
    elif 'modify' in request.form:
        modify_comment('modify', request.form['modify'], request.form)
    else:
        execute_query(
            "INSERT INTO comments (book_id, comment, rating) VALUES (?, ?, ?)",
            [book_id, request.form['comment'], request.form['rating']],
            commit=True
        )
    return redirect(f"/livre?id={book_id}", 303)
