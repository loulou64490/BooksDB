from app import app, db
from flask import render_template, request, redirect, flash, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import execute_query, User, generate_date, val_email, Book, Comment, val_comment, val_book, val_user
from werkzeug.security import generate_password_hash, check_password_hash


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def not_found(e):
    flash('ERREUR')
    return redirect(url_for('index')), 500


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


@app.route('/recherche')
def search():
    query = request.args.get('q')
    if query:
        data = execute_query(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ?",
            ['%' + query + '%'] * 3, fetchall=True
        )
        if len(data) == 1:
            return redirect(url_for('book', id=data[0]['id']))

    else:
        data = execute_query("SELECT * FROM books", fetchall=True)
    return render_template('search.html', data=data, query=query)


@app.route('/connexion')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = session.pop("login_data", {})
    if form:
        errors = None
        if not form['email'] or not form['password']:
            errors = 'Veuillez remplir tous les champs'
        elif not val_email(form['email']):
            errors = 'Adresse mail invalide'

        if form['submit'] == 'login':
            ex_user = User.query.filter_by(email=form['email']).first()
            if not (ex_user and check_password_hash(ex_user.hash, form['password'])):
                errors = 'Adresse mail ou mot de passe incorrect'
            if errors:
                return render_template('login.html', errors=errors, email=form['email'])

            login_user(ex_user, remember=True)
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

            new_user = User(name=form['name'], hash=generate_password_hash(form['password']), email=form['email'])
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Inscription réussie')
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/post_connexion', methods=['POST'])
def post_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    session["login_data"] = request.form.to_dict()
    return redirect(url_for("login"))


@app.route("/compte")
@login_required
def account():
    return render_template('account.html')


@app.route("/utilisateur")
def user():
    user_id = request.args.get('id')
    data = execute_query("SELECT * FROM users WHERE id=?", [user_id], fetchone=True)
    if data:
        books = execute_query("SELECT * FROM books WHERE user_id=? limit 5", [user_id], fetchall=True)
        comments = execute_query(
            "SELECT comments.id, comment, rating, comments.date, title, author, book_id FROM comments join books on comments.book_id = books.id WHERE comments.user_id=? ORDER BY comments.id DESC limit 5",
            [user_id], fetchall=True)
        return render_template('user.html', data=data, books=books, comments=comments, date=generate_date(comments))
    flash('L\'utilisateur a surement été supprimé')
    return render_template('errors/404.html'), 404

@app.route("/post_utilisateur", methods=['POST'])
@login_required
def post_user():
    form = request.form.to_dict()
    if form['user_id'] and form['type'] == 'signal':
        execute_query("update users set signal=signal+1 where id=?",[form['user_id']], commit=True)
        flash("Utilisateur signalé")
        return redirect(url_for('user', id=form['user_id']))
    flash("ERREUR")
    return redirect(url_for('index'))



@app.route("/post_compte", methods=['POST'])
@login_required
def post_account():
    form = request.form.to_dict()
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
    return redirect(url_for('account'))


@app.context_processor
def inject_add_book():
    return {'book': Book()}


@app.route('/livre')
def book():
    book_id = request.args.get('id')
    data = execute_query("SELECT * FROM books WHERE id=?", [book_id], fetchone=True)
    if data:
        comments = execute_query(
            "SELECT comments.id, comment, rating, comments.date, name, user_id FROM comments join users on comments.user_id = users.id WHERE book_id=? ORDER BY comments.id DESC",
            [book_id], fetchall=True)
        if comments:
            average = round(
                execute_query("SELECT AVG(rating) FROM comments WHERE book_id=?", [book_id], fetchone=True)[0], 1)
            if average.is_integer():
                average = int(average)
            mod_comm_form = {}
            for i in comments:
                mod_comm_form[i['id']] = Comment()
                mod_comm_form[i['id']].content.data, mod_comm_form[i['id']].rating.data = i['comment'], i['rating']
            return render_template('book.html', comm=Comment(), data=data, comments=comments, average=average,
                                   date=generate_date(comments))
        return render_template('book.html', comm=Comment(), data=data)
    flash('Le livre a surement été supprimé')
    return render_template('errors/404.html'), 404


@app.route('/post_livre', methods=['POST'])
@login_required
def post_book():
    result = Book()
    form = {}
    for i in result:
        if i.data is not None:
            form[i.name] = i.data
    actions = {
        'add': {
            'validate': lambda: result.validate_on_submit(),
            'query': "INSERT INTO books (title, author, year, user_id) VALUES (?, ?, ?, ?)",
            'params': lambda: [form['title'], form['author'], form['year'], current_user.id],
            'flash': 'Livre ajouté'
        },
        'modify': {
            'validate': lambda: result.validate_on_submit() and val_book(form['book_id'], True),
            'query': "UPDATE books SET title=?, author=?, year=? WHERE id=?",
            'params': lambda: [form['title'], form['author'], form['year'], form['book_id']],
            'flash': 'Livre modifié'
        },
        'delete': {
            'validate': lambda: val_book(form['book_id'], True),
            'query': "DELETE FROM books WHERE id=?",
            'params': lambda: [form['book_id']],
            'flash': 'Livre supprimé'
        },
        'signal': {
            'validate': lambda: val_book(form['book_id']),
            'query': "UPDATE books SET signal=signal+1 WHERE id=?",
            'params': lambda: [form['book_id']],
            'flash': 'Livre signalé'
        }
    }
    for action, details in actions.items():
        if action == form['type']:
            if details['validate']():
                execute_query(details['query'], details['params'](), commit=True)
                flash(details['flash'])
                if action == 'add':
                    form['book_id'] = execute_query("SELECT id FROM books order by id desc limit 1", fetchone=True)[
                        0]
                elif action == 'delete':
                    return redirect(url_for('index'))
                return redirect(url_for('book', id=form['book_id']))
    flash('ERREUR')
    return redirect(url_for('index'))


@app.route('/post_comment', methods=['POST'])
@login_required
def post_comment():
    result = Comment()
    form = {}
    for i in result:
        if i.data is not None:
            form[i.name] = i.data
    actions = {
        'add': {
            'validate': lambda: result.validate_on_submit() and val_book(form['book_id']),
            'query': "INSERT INTO comments (book_id, comment, rating,user_id) VALUES (?, ?, ?,?)",
            'params': lambda: [form['book_id'], form['content'], form['rating'], current_user.id],
            'flash': 'Commentaire publié'
        },
        'modify': {
            'validate': lambda: result.validate_on_submit() and val_comment(form['comm_id'], True),
            'query': "UPDATE comments SET comment=?, rating=? WHERE id=?",
            'params': lambda: [form['content'], form['rating'], form['comm_id']],
            'flash': 'Commentaire modifié'
        },
        'delete': {
            'validate': lambda: val_comment(form['comm_id'], True),
            'query': "DELETE FROM comments WHERE id=?",
            'params': lambda: [form['comm_id']],
            'flash': 'Commentaire supprimé'
        },
        'signal': {
            'validate': lambda: val_comment(form['comm_id']),
            'query': "UPDATE comments SET signal=signal+1 WHERE id=?",
            'params': lambda: [form['comm_id']],
            'flash': 'Commentaire signalé'
        }
    }
    for action, details in actions.items():
        if action == form['type']:
            if details['validate']():
                execute_query(details['query'], details['params'](), commit=True)
                flash(details['flash'])
                return redirect(url_for('book', id=form['book_id']))
    flash('ERREUR')
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin():
    if current_user.admin == 0:
        return render_template('errors/404.html'), 404
    data = {
        'books': execute_query(
            "SELECT books.id, title, author, year, name FROM books join users on books.user_id = users.id where books.signal>0 order by books.signal desc",
            fetchall=True),
        'comments': execute_query(
            "SELECT comments.id, comment, rating, name, title, author, comments.date FROM comments join users on users.id = comments.user_id join books on books.id = book_id where comments.signal>0 order by comments.signal desc",
            fetchall=True),
        'users': execute_query("SELECT id, name, email FROM users where signal>0 order by users.signal desc",
                               fetchall=True)
    }
    return render_template('admin.html', data=data, date=generate_date(data['comments']))


@app.route('/post_admin', methods=['POST'])
@login_required
def post_admin():
    if current_user.admin == 0:
        return render_template('errors/404.html'), 404
    form = request.form.to_dict()
    actions = {
        'book': {
            'delete': {
                'validate': lambda: val_book(form['delete']),
                'query': "DELETE FROM books WHERE id=?",
                'params': lambda: [form['delete']],
                'flash': 'Livre supprimé'
            },
            'validate': {
                'validate': lambda: val_book(form['validate']),
                'query': "UPDATE books SET signal=0 WHERE id=?",
                'params': lambda: [form['validate']],
                'flash': 'Livre validé'
            }
        },
        'comment': {
            'delete': {
                'validate': lambda: val_comment(form['delete']),
                'query': "DELETE FROM comments WHERE id=?",
                'params': lambda: [form['delete']],
                'flash': 'Commentaire supprimé'
            },
            'validate': {
                'validate': lambda: val_comment(form['validate']),
                'query': "UPDATE comments SET signal=0 WHERE id=?",
                'params': lambda: [form['validate']],
                'flash': 'Commentaire validé'
            }
        },
        'user': {
            'delete': {
                'validate': lambda: val_user(form['delete']),
                'query': "DELETE FROM users WHERE id=?",
                'params': lambda: [form['delete']],
                'flash': 'Utilisateur supprimé'
            },
            'validate': {
                'validate': lambda: val_user(form['validate']),
                'query': "UPDATE users SET signal=0 WHERE id=?",
                'params': lambda: [form['validate']],
                'flash': 'Utilisateur validé'
            }
        }
    }
    for action_type, action_content in actions.items():
        if action_type == form['type']:
            for action, details in action_content.items():
                if action in form:
                    if details['validate']():
                        execute_query(details['query'], details['params'](), commit=True)
                        flash(details['flash'])
                        return redirect(url_for('admin'))
    flash('ERREUR')
    return redirect(url_for('index'))
