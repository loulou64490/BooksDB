import sqlite3
import ollama #TODO : ajouter de l'ia
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/')
def accueil():
    return render_template('index.html', )


@app.route('/nouveau')
def nouveau():
    return render_template('nouveau.html', )

@app.route('/ajouter', methods=['POST'])
def ajouter():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute("select * from books where title like ? or author like ? or year like ? or comment like ?",)
    data=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return redirect("livre?",303)

@app.route('/livre',methods=['GET'])
def livre():
    conn=get_db_connection()
    cur=conn.cursor()
    data=cur.execute("select * from books where id=?",[request.args.get('id')]).fetchone()
    cur.close()
    conn.close()
    return render_template('livre.html', data=data)

@app.route('/recherche', methods=['POST'])
def recherche():
    conn=get_db_connection()
    cur=conn.cursor()
    data=cur.execute("select * from books where title like ? or author like ? or year like ? or comment like ?",['%'+request.form['query']+'%' for i in range(4)]).fetchall()
    cur.close()
    conn.close()
    return render_template('recherche.html', data=data, result=request.form['query'])

@app.route('/supprimer', methods=['POST'])
def supprimer():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute("delete from books where id=?",[request.args.get('id')])
    conn.commit()
    cur.close()
    conn.close()
    return redirect("livre?",303)

@app.route('/modifier', methods=['POST'])
def modifier():
    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute("") # TODO : compléter la requête
    conn.commit()
    cur.close()
    conn.close()
    return redirect("livre?",303)

if __name__ == '__main__':
    app.run(debug=True)
