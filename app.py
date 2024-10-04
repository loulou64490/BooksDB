import sqlite3
import ollama  # TODO : ajouter de l'ia
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

# TODO: page d'accueil
@app.route('/')
def accueil():
    return render_template('index.html', )


@app.route('/livre', )
def livre():
    if request.args.get('id'):
        conn = get_db_connection()
        cur = conn.cursor()
        data = cur.execute("select * from books where id=?", [request.args.get('id')]).fetchone()
        cur.close()
        conn.close()
        return render_template('livre.html', data=data)
    else:
        return redirect("recherche", 303)


@app.route('/recherche', methods=['POST', 'GET'])
def recherche():
    if request.form['query'] != '':
        conn = get_db_connection()
        cur = conn.cursor()
        data = cur.execute("select * from books where title like ? or author like ? or year like ? or comment like ?",
                           ['%' + request.form['query'] + '%' for i in range(4)]).fetchall()
        cur.close()
        conn.close()
        return render_template('recherche.html', data=data, result=request.form['query'])
    else:
        return render_template('recherche.html', )


# TODO: suppression d'un livre
# cur.execute("delete from books where id=?", [request.args.get('id')])
@app.route('/modifier', methods=['POST', 'GET'])
def modifier():
    if request.method == 'POST':
        if request.args.get('id'):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("update books set title=?, author=?, year=? where id=?",
                        [request.form['title'], request.form['author'], request.form['year'], request.args.get('id')])
            conn.commit()
            cur.close()
            conn.close()
            return redirect("livre?id=" + request.args.get('id'), 303)
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("insert into books (title, author, year) values (?, ?, ?); ",
                        [request.form['title'], request.form['author'], request.form['year']])
            idl = cur.lastrowid
            conn.commit()
            cur.close()
            conn.close()
            return redirect("livre?id=" + str(idl), 303)
    else:
        if request.args.get('id'):
            conn = get_db_connection()
            cur = conn.cursor()
            data = cur.execute("select title, author, year from books where id=?", [request.args.get('id')]).fetchone()
            cur.close()
            conn.close()
            return render_template('modifier.html', data=data, id=request.args.get('id'))
        else:
            return render_template('modifier.html', )


if __name__ == '__main__':
    app.run(debug=True)
