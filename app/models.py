import sqlite3
from time import time
from flask_login import UserMixin, current_user
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


def val_email(email): return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', email))


def val_form(form, **expected_fields):
    # toutes les données sont des chaînes de caractères
    # donc on tente de les convertir en celle qui sont attendues
    for field_name, expected_type in expected_fields.items():
        if field_name not in form: return False
        value = form[field_name]
        if expected_type == int:
            if not value.isdigit():
                return False
        elif expected_type == str:
            if not isinstance(value, expected_type):
                return False
        else:
            raise ValueError('Type de données non supporté')
    return True


def val_book(val, own=False):
    val = execute_query("SELECT user_id FROM books WHERE id=?", (val,), fetchone=True)
    if val:
        if own:
            return current_user.id == val['user_id']
        else:
            return True
    return False


def val_comment(val, own=False):
    val = execute_query("SELECT user_id FROM comments WHERE id=?", (val,), fetchone=True)
    if val:
        if own:
            return current_user.id == val['user_id']
        else:
            return True
    return False


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
