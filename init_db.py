import sqlite3


def init_db(add_books=False):
    conn = sqlite3.connect('books.db')
    cur = conn.cursor()
    cur.execute('''create table books (
                        id     INTEGER
                            primary key autoincrement,
                        title  TEXT    not null,
                        author TEXT    not null,
                        year   INTEGER not null
                    );''')
    cur.execute('''create table comments (
                        id      INTEGER
                            primary key autoincrement,
                        book_id INTEGER
                            references books
                                on delete cascade,
                        comment TEXT    not null,
                        rating  INTEGER not null,
                        signal INTEGER default 0,
                        check (rating >= 0 AND rating <= 5)
                    );''')
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
        cur.executemany("insert into comments(book_id, comment, rating) values (?,?,?)", [
            (1,"Une œuvre poignante qui explore les dangers du totalitarisme. Un incontournable pour tous ceux qui s'intéressent à la liberté et à la vérité.",5),
            (1, "L'atmosphère oppressante de ce livre m'a vraiment marqué. Un regard troublant sur un futur possible.",4),
            (1,"Le style d'écriture d'Orwell est captivant, mais l'histoire est si déprimante que je ne sais pas si je le relirai.",3),
            (1,"1984 est un livre qui reste d'actualité. La surveillance de masse décrite est encore plus pertinente aujourd'hui.",5),
            (1,"Les personnages sont bien développés et leurs luttes sont profondément émouvantes. Une lecture difficile mais nécessaire.",4),
            (1,"Un roman qui me fait réfléchir sur la société moderne. La manipulation de l'information est effrayante.",5),
            (1,"J'ai trouvé certaines parties un peu lentes, mais l'impact final en vaut la peine. Une critique forte de l'autoritarisme.",3),
            (1, "Une dystopie qui m'a terrifié. La capacité d'Orwell à prédire notre avenir est impressionnante.", 4),
            (1, "Un livre qui soulève des questions essentielles sur le pouvoir et la vérité. J'ai beaucoup appris.", 5),
            (1,"La notion de 'Big Brother' a pris une nouvelle signification pour moi après cette lecture. Un classique indéniable.",5)
        ])
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    init_db(add_books=True)
