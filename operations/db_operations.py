import sqlite3


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_data(querry: str) -> list:
    with sqlite3.connect('bd_excharngers.sqlite3') as db:
        db.row_factory = dict_factory
        cursor = db.cursor()
        cursor.execute(querry)
        res = cursor.fetchall()
    return res


def write_data_to_DB(querry: str) -> None:
    with sqlite3.connect('bd_excharngers.sqlite3') as db:
        cursor = db.cursor()
        cursor.execute(querry)
        db.commit()


def delete_data_from_DB(querry: str) -> None:
    with sqlite3.connect('bd_excharngers.sqlite3') as db:
        cursor = db.cursor()
        cursor.execute(querry)
        db.commit()