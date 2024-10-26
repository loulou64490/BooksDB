from app import app, db
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models import execute_query, handle_modification, modify_comment, User, generate_date
from werkzeug.security import generate_password_hash, check_password_hash


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.route('/')
def index():
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


@app.route('/connexion', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if request.form['submit'] == 'login':
            user = User.query.filter_by(email=request.form['email']).first()
            if user and check_password_hash(user.hash, request.form['password']):
                login_user(user, remember=True)
                flash('Connexion réussie')
                if request.args.get('next'):
                    return redirect(request.args.get('next'))
                return redirect(url_for('index'))
            else:
                return render_template('login.html', errors='Adresse mail ou mot de passe incorrect',
                                       email=request.form['email'])
        elif request.form['submit'] == 'register':
            if User.query.filter_by(email=request.form['email']).first():
                return render_template('login.html', errors='Email déjà utilisé', name=request.form['name'],
                                       register=True)
            user = User(name=request.form['name'], hash=generate_password_hash(request.form['password']),
                        email=request.form['email'])
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Inscription réussie')
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route("/compte", methods=['POST', 'GET'])
@login_required
def account():
    if request.method == 'POST':
        if request.form['submit'] == 'logout':
            logout_user()
            flash('Déconnexion réussie')
            return redirect(url_for('index'))
        elif request.form['submit'] == 'password':
            if check_password_hash(current_user.hash, request.form['password']):
                current_user.hash = generate_password_hash(request.form['new_password'])
                db.session.commit()
                flash('Mot de passe modifié')
            else:
                flash('Mot de passe incorrect')
        elif request.form['submit'] == 'name':
            current_user.name = request.form['name']
            db.session.commit()
            flash('Nom modifié')
    return render_template('account.html')


@app.route('/livre')
def livre():
    book_id = request.args.get('id')
    data = execute_query("SELECT * FROM books WHERE id=?", [book_id], fetchone=True)
    if data:
        comments = execute_query(
            "SELECT comments.id, comment, rating, date, name, user_id FROM comments join users on comments.user_id = users.id WHERE book_id=? ORDER BY comments.id DESC",
            [book_id], fetchall=True)
        if comments:
            average = round(
                execute_query("SELECT AVG(rating) FROM comments WHERE book_id=?", [book_id], fetchone=True)[0], 1)
            if average.is_integer():
                average = int(average)
            return render_template('book.html', data=data, comments=comments, average=average, date=generate_date(comments))
        else:
            return render_template('book.html', data=data)
    else:
        return render_template('errors/404.html'), 404


@app.route('/recherche', methods=['POST', 'GET'])
def search():
    query = request.form['query']
    if request.method == 'POST' and request.form['query']:
        data = execute_query(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ?",
            ['%' + query + '%'] * 3, fetchall=True
        )
        if len(data) == 1:
            return redirect(url_for('livre', id=data[0]['id']))
    else:
        data = execute_query("SELECT * FROM books", fetchall=True)
    return render_template('search.html', data=data, result=query)


@app.route('/modifier', methods=['POST'])
@login_required
def modify():
    book_id = request.args.get('id')
    if 'delete' in request.form:
        if current_user.id != execute_query("SELECT user_id FROM books WHERE id=?", [book_id], fetchone=True)[0]:
            flash('ERREUR')
            return redirect(url_for('livre', id=book_id))
        else:
            handle_modification(request.form, book_id, delete=True)
            return redirect(url_for('index'))
    else:
        book_id = handle_modification(request.form, book_id, user_id=current_user.id)
        return redirect(url_for('livre', id=book_id))


@app.route('/commenter', methods=['POST'])
@login_required
def comment():
    book_id = request.args.get('id')
    if 'delete' in request.form:
        if current_user.id == execute_query("SELECT user_id FROM comments WHERE id=?", [request.form['delete']],fetchone=True)[0]:
            modify_comment('delete', request.form['delete'])
        else:
            flash('ERREUR')
    elif 'signal' in request.form:
        modify_comment('signal', request.form['signal'])
    elif 'modify' in request.form:
        if current_user.id == execute_query("SELECT user_id FROM comments WHERE id=?", [request.form['modify']],fetchone=True)[0]:
            modify_comment('modify', request.form['modify'], request.form)
        else:
            flash('ERREUR')
    else:
        execute_query(
            "INSERT INTO comments (book_id, comment, rating,user_id) VALUES (?, ?, ?,?)",
            [book_id, request.form['comment'], request.form['rating'], current_user.id],
            commit=True
        )
    return redirect(url_for('livre', id=book_id))
