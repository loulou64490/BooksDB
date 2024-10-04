import sqlite3

def init_db(add_books=False):
    conn = sqlite3.connect('books.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL , 
                    author TEXT NOT NULL, 
                    year TEXT NOT NULL, 
                    rate INTEGER,
                    comment TEXT
                    )''')
    if add_books:
        cur.executemany("insert into books(title,author,year) values(?, ?, ?)", [
            ("1984", "Orwell", 1949),
            ("Dune", "Herbert", 1965),
            ("Fondation", "Asimov", 1951),
            ("Le meilleur des mondes", "Huxley", 1931),
            ("Fahrenheit 451", "Bradbury", 1953),
            ("Ubik", "K.Dick", 1969),
            ("Chroniques martiennes", "Bradbury", 1950),
            ("La nuit des temps", "Barjavel", 1968),
            ("Blade Runner", "K.Dick", 1968),
            ("Les Robots", "Asimov", 1950),
            ("La Planète des singes", "Boulle", 1963),
            ("Ravage", "Barjavel", 1943),
            ("Le Maître du Haut Château", "K.Dick", 1962),
            ("Le monde des Ā", "Van Vogt", 1945),
            ("La Fin de l'éternité", "Asimov", 1955),
            ("De la Terre à la Lune", "Verne", 1865)
        ])
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    init_db()