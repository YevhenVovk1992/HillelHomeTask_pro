import sqlite3

def get_data(querry: str):
    with sqlite3.connect('bd_excharngers.sqlite3') as db:
        cursor = db.execute(querry)
        res = cursor.fetchall()
    return res