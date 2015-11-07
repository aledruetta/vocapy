#! /usr/bin/env python3

import sqlite3 as sql
import csv

_database = '../../database.db'


def populate_db():
    """
    Populates database.db para pruebas.
    """

    words = list()

    with open('dict.txt', newline='') as csvfile:
        for row in csv.reader(csvfile):
            word, last_time, attempts, guess = row[:4]
            means = set(row[4:])
            words.append((word, 0.0, 0, 0, means))

    conn = sql.connect(_database)
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        for word, last_time, attempts, guess, means in words:
            cur.execute("INSERT INTO words VALUES (?, ?, ?, ?)",
                        (word, last_time, attempts, guess))
            for mean in means:
                cur.execute("INSERT INTO means VALUES(?, ?)", (word, mean))
        conn.commit()
        print(cur.execute("SELECT * FROM words").fetchall())
        print(cur.execute("SELECT * FROM means").fetchall())


def main():
    populate_db()

if __name__ == "__main__":
    main()
