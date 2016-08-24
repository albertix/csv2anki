import sqlite3, os

databaseFile = 'example.db'
if os.path.isfile(databaseFile):
    os.remove(databaseFile)

conn = sqlite3.connect(databaseFile)


def init(sql_file):
    with open(sql_file, 'r') as f:
        sqls = f.read()
        c = conn.cursor()
        c.executescript(sqls)
        conn.commit()
        c.close()
        conn.close()


if __name__ == '__main__':
    init('../demo3.sql')
