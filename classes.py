#! /usr/bin/env python3

# Script Name:          classes.py
# Author:               Alejandro Druetta
# Version:              0.2
#
# Description:          Aplicación para el aprendizaje de vocabulario de
#                       lenguas extranjeras.

import time
import subprocess
from operator import itemgetter
import sqlite3 as sql
import random

DATABASE = 'database.db'
_PRAGMA = "PRAGMA foreign_keys = ON"


class VocapyWord:
    """Objeto que representa cada palabra de la lengua aprendida"""

    def __init__(self, name, last_time, attempts, guess, means):
        self.name = name
        self.last_time = last_time
        self.attempts = attempts
        self.guess = guess
        self.means = means

    @property
    def percent(self):
        """Porcentaje de aciertos en relación a la cantidad de intentos"""
        try:
            return int(self.guess * 100 / self.attempts)
        except ZeroDivisionError:
            return 0
        except TypeError:
            return 0

    def rand_mean(self):
        """Uno de los significados de la palabra al azar"""
        return random.choice(self.means)

    def update_db(self):
        """Actualiza los datos en DB del objeto VocapyWord"""
        self.last_time = time.time()        # Actualiza el tiempo
        conn = sql.connect(DATABASE)       # de visualización
        with conn:
            cur = conn.cursor()
            cur.execute(_PRAGMA)
            cur.execute("UPDATE words SET last_time=?, attempts=?, guess=? \
                        WHERE word_ID=?", (
                            self.last_time,
                            self.attempts,
                            self.guess,
                            self.name
                        )
                        )
            conn.commit()

    def __repr__(self):
        return "VocapyWord: {}, {}, {}, {}, {}".format(
            self.name,
            self.last_time,
            self.attempts,
            self.guess,
            self.means
        )


class WordList(list):
    """Lista de objetos VocapyWord"""

    def __init__(self):
        self.db_load()
        self.length = len(self)

    def db_load(self):
        """Construye WordList a partir de los datos en DB"""
        conn = sql.connect(DATABASE)
        with conn:
            cur = conn.cursor()
            word_list = cur.execute("SELECT * FROM words").fetchall()
            for name, last_time, attempts, guess in word_list:
                means = cur.execute(
                    "SELECT mean_ID FROM means WHERE word_ID = ?", (name,)
                ).fetchall()
                # fetchall devuelve una lista de tuplas de un
                # elemento (element,)
                means = [m[0] for m in means]
                self.append(
                    VocapyWord(name, last_time, attempts, guess, means)
                )

    def append_db(self, word):
        """Agrega un elemento a WordList"""
        conn = sql.connect(DATABASE)
        with conn:
            cur = conn.cursor()
            cur.execute(_PRAGMA)
            cur.execute("INSERT INTO words VALUES (?, ?, ?, ?)",
                        (word.name, word.last_time, word.attempts,
                         word.guess))
            for mean in word.means:
                cur.execute("INSERT INTO means VALUES (?, ?)",
                            (word.name, mean))
            conn.commit()
        super().append(word)

    def remove_db(self, word):
        """Remueve un elemento de WordList"""
        conn = sql.connect(DATABASE)
        with conn:
            cur = conn.cursor()
            cur.execute(_PRAGMA)
            cur.execute("DELETE FROM means WHERE word_ID=?",
                        (word.name,))
            cur.execute("DELETE FROM words WHERE word_ID=?",
                        (word.name,))
            conn.commit()
        super().remove(word)

    def clear(self):
        """Limpia WordList y la base de datos"""
        super().clear()
        subprocess.call(['rm', DATABASE])
        subprocess.check_output("cat schema.sql | sqlite3 {}".format(DATABASE),
                                shell=True)

    def sort_by_attr(self, attr):
        """Ordena WordList por atributo de VocapyWord"""
        # Lista de tuplas con formato (palabra, atributo)
        word_attr = [(word, word.__getattribute__(attr)) for word in self]
        # itemgetter(1) permite ordenar por el segundo elemento de
        # cada tupla (atributo).
        word_attr.sort(key=itemgetter(1))

        return [word for word, attribute in word_attr]

    @property
    def oldest(self):
        """El elemento que lleva más tiempo sin ser visualizado"""
        return self.sort_by_attr('last_time')[0]

    @property
    def worst(self):
        """El elemento con peor porcentaje"""
        return self.sort_by_attr('percent')[0]

    @property
    def random(self):
        """Un elemento aleatóreamente escogido"""
        return random.choice(self)


class GameRound:
    """Objeto representando cada una de las rondas de juego"""

    def __init__(self, word_list):
        self._word_list = word_list         # WordList instance
        self.word = self.select_word()
        self.target = self.word.rand_mean()
        self.means = self.select_choices()

    def select_word(self):
        """Escoge un elemento entre tres criterios posibles:
            - El menos visualizado
            - El que tiene peor porcentaje
            - Un elemento aleatóreo
        """
        self.oldest = self._word_list.oldest
        self.worst = self._word_list.worst
        self.random = self._word_list.random

        return random.choice([self.oldest, self.worst, self.random])

    def select_choices(self):
        """Selecciona las opciones presentadas al jugador"""
        means_set = {self.target}
        while len(means_set) < 4:
            rand_word = self._word_list.random
            fake = rand_word.rand_mean()
            if fake not in self.word.means:
                means_set.add(fake)
        means_lst = list(means_set)
        random.shuffle(means_lst)

        return means_lst

    def __repr__(self):
        return """
    {}
    Oldest: {} [last_time: {}]
    Worst:  {} [percent: {}]
    Random: {}""".format(
            self.word.name, self.oldest.name, self.oldest.last_time,
            self.worst.name, self.worst.percent, self.random.name
            )


class Session:

    def __init__(self, last_time, attempts, guess):
        self.last_time = last_time
        self.attempts = attempts
        self.guess = guess

    @property
    def percent(self):
        try:
            return int(self.guess * 100 / self.attempts)
        except ZeroDivisionError:
            return 0
        except TypeError:
            return 0

    @property
    def sessions_lst(self):
        conn = sql.connect(DATABASE)
        with conn:
            cur = conn.cursor()
            fetch = cur.execute("SELECT * FROM sessions").fetchall()
            fetch.sort(key=itemgetter(0))
            return fetch

    def append_db(self):
        if self.attempts:
            conn = sql.connect(DATABASE)
            with conn:
                cur = conn.cursor()
                cur.execute(_PRAGMA)
                cur.execute("INSERT INTO sessions VALUES (?, ?, ?)", (
                    self.last_time, self.attempts, self.guess))
                conn.commit()


class PercentBar:

    def __init__(self, text, start, lenght, char, percent, colors):
        self.text = text        # Object tk.Text
        self.start = start      # Coords Tuple, ex: (1, 0)
        self.lenght = lenght
        self.char = char
        self.percent = percent
        self.colors = colors    # Colors Tuple, ex: ('green', 'red')

    def create(self):
        self.text.tag_configure('segment1', background=self.colors[0])
        self.text.tag_configure('segment2', background=self.colors[1])

        segment1 = round(self.percent * self.lenght / 100) * self.char
        segment2 = (self.lenght - len(segment1)) * self.char

        row = self.start[0]
        column = self.start[1]
        forward = column + len(segment1)

        seg1_start = '{}.{}'.format(row, column)
        seg1_end = '{}.{}'.format(row, forward)

        seg2_start = '{}.{}'.format(row, forward)
        seg2_end = '{}.{}'.format(row, forward + len(segment2))

        self.text.insert(seg1_start, segment1 + segment2)
        self.text.tag_add('segment1', seg1_start, seg1_end)
        self.text.tag_add('segment2', seg2_start, seg2_end)


def main():
    pass

if __name__ == "__main__":
    main()
