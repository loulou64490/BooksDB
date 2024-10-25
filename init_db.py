import sqlite3



def init_db(add_content=False):
    conn = sqlite3.connect('instance/books.db')
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
                        user_id INTEGER
                            references users
                                on delete cascade,
                        date    INTEGER   default (strftime('%s', 'now')),
                        signal INTEGER default 0,
                        check (rating >= 0 AND rating <= 5)
                    );''')
    cur.execute('''create table users (
                        id      INTEGER
                            primary key autoincrement,
                        name    TEXT    not null,
                        hash    TEXT    not null,
                        email   TEXT    unique not null
                    );''')
    cur.execute("create index idx_book_id on comments(book_id);")
    if add_content:
        cur.execute("insert into users(name, hash, email) values(?,?,?)",("Louis Chauvet-Villaret","test","louis@revuejazz.fr"))
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
        cur.executemany("insert into comments(book_id, comment, user_id, rating) values (?,?,?,?)", [
            (1,"Une œuvre poignante qui explore les dangers du totalitarisme. Un incontournable pour tous ceux qui s'intéressent à la liberté et à la vérité.",1,5),
            (1, "L'atmosphère oppressante de ce livre m'a vraiment marqué. Un regard troublant sur un futur possible.",1,4),
            (1,"Le style d'écriture d'Orwell est captivant, mais l'histoire est si déprimante que je ne sais pas si je le relirai.",1,3),
            (1,"1984 est un livre qui reste d'actualité. La surveillance de masse décrite est encore plus pertinente aujourd'hui.",1,5),
            (1,"Les personnages sont bien développés et leurs luttes sont profondément émouvantes. Une lecture difficile mais nécessaire.",1,4),
            (1,"Un roman qui me fait réfléchir sur la société moderne. La manipulation de l'information est effrayante.",1,5),
            (1,"J'ai trouvé certaines parties un peu lentes, mais l'impact final en vaut la peine. Une critique forte de l'autoritarisme.",1,3),
            (1, "Une dystopie qui m'a terrifié. La capacité d'Orwell à prédire notre avenir est impressionnante.",1, 4),
            (1, "Un livre qui soulève des questions essentielles sur le pouvoir et la vérité. J'ai beaucoup appris.",1, 5),
            (1,"La notion de 'Big Brother' a pris une nouvelle signification pour moi après cette lecture. Un classique indéniable.",1,5)
        ])
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    init_db(add_content=True)
