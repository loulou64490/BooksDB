from sqlite3 import IntegrityError
from app import app, db
from flask import render_template, request, redirect, flash, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import execute_query, User, generate_date, val_email, val_form, val_book, val_comment
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


# décorateur post/redirect/get
def prg(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            session.setdefault("form_data", {})
            for key, value in request.form.items():
                session["form_data"][key] = value
            return redirect(request.url)
        data = session.pop("form_data", {})
        return func(form=data, *args, **kwargs)

    return decorated_function


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
            "SELECT books.id, title, comment, rating "
            "FROM books LEFT JOIN comments ON books.id=comments.book_id "
            "ORDER BY comments.id DESC LIMIT 5", fetchall=True)
    }
    return render_template('index.html', data=data)


@app.route('/connexion', methods=['POST', 'GET'])
@prg
def login(form=None):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form:
        errors = None
        if not form['email'] or not form['password']:
            errors = 'Veuillez remplir tous les champs'
        elif not val_email(form['email']):
            errors = 'Adresse mail invalide'

        if form['submit'] == 'login':
            user = User.query.filter_by(email=form['email']).first()
            if not (user and check_password_hash(user.hash, form['password'])):
                errors = 'Adresse mail ou mot de passe incorrect'
            if errors:
                return render_template('login.html', errors=errors, email=form['email'])

            login_user(user, remember=True)
            flash('Connexion réussie')
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            return redirect(url_for('index'))


        elif form['submit'] == 'register':
            if not form['name']:
                errors = 'Veuillez remplir tous les champs'
            elif User.query.filter_by(email=form['email']).first():
                errors = 'Adresse mail déjà utilisée'
            if errors:
                return render_template('login.html', errors=errors, name=form['name'],
                                       email=form['email'], register=True)

            user = User(name=form['name'], hash=generate_password_hash(form['password']), email=form['email'])
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Inscription réussie')
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route("/compte", methods=['POST', 'GET'])
@login_required
@prg
def account(form=None):
    if form:
        if form['submit'] == 'logout':
            logout_user()
            flash('Déconnexion réussie')
            return redirect(url_for('index'))
        elif form['submit'] == 'password':
            if check_password_hash(current_user.hash, form['password']):
                current_user.hash = generate_password_hash(form['new_password'])
                db.session.commit()
                flash('Mot de passe modifié')
            else:
                flash('Mot de passe incorrect')
        elif form['submit'] == 'name':
            current_user.name = form['name']
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
            return render_template('book.html', data=data, comments=comments, average=average,
                                   date=generate_date(comments))
        return render_template('book.html', data=data)
    return render_template('errors/404.html'), 404


@app.route('/recherche', methods=['POST', 'GET'])
@prg
def search(form=None):
    if form:
        data = execute_query(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ?",
            ['%' + form['query'] + '%'] * 3, fetchall=True
        )
        if len(data) == 1:
            return redirect(url_for('livre', id=data[0]['id']))
    else:
        data = execute_query("SELECT * FROM books", fetchall=True)
    return render_template('search.html', query=form['query'], data=data)


@app.route('/modifier', methods=['POST'])
@login_required
def modify():
    book_id = request.args.get('id')
    if 'delete' in request.form:
        if current_user.id != execute_query("SELECT user_id FROM books WHERE id=?", [book_id], fetchone=True)[0]:
            flash('ERREUR')
            return redirect(url_for('livre', id=book_id))
        else:
            execute_query("DELETE FROM books WHERE id=?", [book_id], commit=True)
            flash('Livre supprimé')
            return redirect(url_for('index'))
    else:
        if book_id:
            if current_user.id != execute_query("SELECT user_id FROM books WHERE id=?", [book_id], fetchone=True)[0]:
                execute_query(
                    "UPDATE books SET title=?, author=?, year=? WHERE id=?",
                    [request.form['title'], request.form['author'], request.form['year'], book_id],
                    commit=True
                )
                flash('Livre modifié')
                return redirect(url_for('livre', id=book_id))
            else:
                flash('ERREUR')
                return redirect(url_for('livre', id=book_id))
        else:
            cur = execute_query(
                "INSERT INTO books (title, author, year, user_id) VALUES (?, ?, ?, ?)",
                [request.form['title'], request.form['author'], request.form['year'], current_user.id],
                commit=True
            )
            book_id = cur.lastrowid
            flash('Livre ajouté')
            return redirect(url_for('livre', id=book_id))


@app.route('/comment', methods=['POST'])
@login_required
def comment():
    form = request.form
    actions = {
        'add': {
            'validate': lambda: val_form(form, comment=str, rating=int, book_id=int) and val_book(form['book_id']),
            'query': "INSERT INTO comments (book_id, comment, rating,user_id) VALUES (?, ?, ?,?)",
            'params': lambda: [form['book_id'], form['comment'], form['rating'], current_user.id]
        },
        'modify': {
            'validate': lambda: val_form(form, comment=str, rating=int, book_id=int) and val_comment(form['comm_id'],
                                                                                                     True),
            'query': "UPDATE comments SET comment=?, rating=? WHERE id=?",
            'params': lambda: [form['comment'], form['rating'], form['comm_id']]
        },
        'delete': {
            'validate': lambda: val_form(form, comm_id=int, book_id=int) and val_comment(form['comm_id'], True),
            'query': "DELETE FROM comments WHERE id=?",
            'params': lambda: [form['comm_id']]
        },
        'signal': {
            'validate': lambda: val_form(form, comm_id=int) and val_comment(form['comm_id']),
            'query': "UPDATE comments SET signal=1 WHERE id=?",
            'params': lambda: [form['comm_id']]
        }
    }
    for action, details in actions.items():
        if action in form:
            if details['validate']():
                execute_query(details['query'], details['params'](), commit=True)
            else:
                flash('ERREUR')
                return redirect(url_for('index'))
    return redirect(url_for('livre', id=form['book_id']))


@app.route('/admin')
@login_required
def admin():
    if current_user.id != 1:
        return render_template('errors/404.html'), 404
    return render_template('admin.html')
