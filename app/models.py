import sqlite3
from select import select
from time import time
from flask_login import UserMixin, current_user
from app import db, login
import re
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField
from wtforms.validators import Length, InputRequired, NumberRange


# from ollama import chat
# import threading

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    date = db.Column(db.Integer, default=time())
    last = db.Column(db.Integer, default=time())
    signal = db.Column(db.Integer, default=0)
    admin = db.Column(db.Integer, default=0)


class Book(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(max=100)])
    author = StringField(validators=[InputRequired(), Length(max=100)])
    year = IntegerField(validators=[InputRequired()])
    type = HiddenField(validators=[InputRequired()])
    book_id = HiddenField()


class Comment(FlaskForm):
    content = TextAreaField(validators=[InputRequired(), Length(max=500)])
    rating = IntegerField(validators=[InputRequired(), NumberRange(min=0, max=5)])
    type = HiddenField(validators=[InputRequired()])
    comm_id = HiddenField()
    book_id = HiddenField(validators=[InputRequired()])


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def val_email(email): return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', email))


def val_book(val, own=False):
    val = execute_query("SELECT user_id FROM books WHERE id=?", (val,), fetchone=True)
    if val:
        if own:
            return current_user.id == val['user_id']
        return True
    return False


def val_comment(val, own=False):
    val = execute_query("SELECT user_id FROM comments WHERE id=?", (val,), fetchone=True)
    if val:
        if own:
            return current_user.id == val['user_id']
        return True
    return False

def val_user(val, not_admin=False):
    val = execute_query("SELECT id, admin FROM users WHERE id=?", (val,), fetchone=True)
    if val:
        if not_admin:
            return not bool(val['admin'])
        return True
    return False


def generate_date_comment(comments):
    date = {}
    for i in comments:
        date[i['id']]=generate_date(i['date'])
    return date

def generate_date(date):
    d = int(time() - date)
    if d < 3600:
        d = str(d // 60) + ' minute'
    elif d < 86400:
        d = str(d // 3600) + ' heure'
    elif d < 604800:
        d = str(d // 86400) + ' jour'
    elif d < 2678400:
        d = str(d // 604800) + ' semaine'
    elif d < 31536000:
        d = str(d // 2678400) + 'mois'
    else:
        d = str(d // 31536000) + ' an'
    if d[0] > '1' and d[-1] != 's':
        d += 's'
    d = 'il y a ' + d
    if d == 'il y a 0 minute':
        d = "à l'instant"
    return d

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    with sqlite3.connect('instance/books.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute(query, params)

        if commit:
            conn.commit()
            return cur

        if fetchone:
            return cur.fetchone()

        if fetchall:
            return cur.fetchall()
        return None

# ai = lambda message:chat(model='qwen2.5:0.5b', messages=[{'role': 'user', 'content': message}, ])['message']['content']
