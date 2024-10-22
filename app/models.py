import sqlite3
from ollama import chat
import threading

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

def handle_modification(data, book_id=None, delete=False):
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
            "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
            [data['title'], data['author'], data['year']],
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

ai = lambda message:chat(model='qwen2.5:0.5b', messages=[{'role': 'user', 'content': message}, ])['message']['content']
