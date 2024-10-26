import sqlite3
from time import time
from flask_login import UserMixin
from app import db, login
import re


# from ollama import chat
# import threading

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def valide_email(email): return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', email))


def generate_date(comments):
    date = {}
    for i in comments:
        d = int(time() - i['date'])
        if d < 3600:
            d = d // 60
            if d == 1:
                d = str(d) + ' minute'
            else:
                d = str(d) + ' minutes'
        elif d < 86400:
            d = d // 3600
            if d == 1:
                d = str(d) + ' heure'
            else:
                d = str(d) + ' heures'
        elif d < 604800:
            d = d // 86400
            if d == 1:
                d = str(d) + ' jour'
            else:
                d = str(d) + ' jours'
        elif d < 2678400:
            d = d // 604800
            if d == 1:
                d = str(d) + ' semaine'
            else:
                d = str(d) + ' semaines'
        elif d < 31536000:
            d = str(d // 2678400) + 'mois'
        else:
            d = d // 31536000
            if d == 1:
                d = str(d) + ' an'
            else:
                d = str(d) + ' ans'
        date[i['id']] = 'il y a ' + d
        if d == '0 minutes':
            date[i['id']] = 'à l\'instant'
    return date


def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    with sqlite3.connect('instance/books.db') as conn:
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


def handle_modification(data, book_id=None, delete=False, user_id=None):
    if delete:
        execute_query("DELETE FROM books WHERE id=?", [book_id], commit=True)
    elif book_id:
        execute_query(
            "UPDATE books SET title=?, author=?, year=? WHERE id=?",
            [data['title'], data['author'], data['year'], book_id],
            commit=True
        )
    else:
        cur = execute_query(
            "INSERT INTO books (title, author, year, user_id) VALUES (?, ?, ?, ?)",
            [data['title'], data['author'], data['year'], user_id],
            commit=True
        )
        book_id = cur.lastrowid
    return book_id


def modify_comment(action, comment_id, form_data=None):
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

# ai = lambda message:chat(model='qwen2.5:0.5b', messages=[{'role': 'user', 'content': message}, ])['message']['content']
