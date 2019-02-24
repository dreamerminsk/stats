import sqlite3

db=sqlite3.connect('releases.db')
c=db.cursor()
c.execute('create table torrents(id int primary key, title string)')
for row in c.execute('select * from sqlite_master'):
    print(row)

db.close()
