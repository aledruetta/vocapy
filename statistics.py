#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Script Name:          statistics.py
# Author:               Alejandro Druetta
# Version:              0.4
#
# Description:          Aplicación para el aprendizaje de vocabulario de
#                       lenguas extranjeras.

import tkinter as tk
from tkinter import messagebox
from classes import Session
from classes import MAXVIEW


class Stats:
    def __init__(self, master):
        self.sessions = Session.sessions_lst()
        if len(self.sessions) > MAXVIEW:
            # Show last MAXVIEW elements
            self.sessions = self.sessions[:MAXVIEW-1]
        # Greatest attempt's length
        attempts_lst = sorted([session.attempts for session in self.sessions])
        try:
            self.max_att = len(str(attempts_lst.pop()))
        except IndexError:
            # Messagebox
            title = _('Advertencia')
            message = _('\nNo hay sesiones previas guardadas \
                        en la base de datos.')
            messagebox.showinfo(title, message, parent=master)
        else:
            self.window = tk.Toplevel(master)
            self.window.title(_('Estadísticas'))
            self.window.resizable(0, 0)
            self.window.bind('<Control-q>', self.destroyWin)

            self.bar_len = 20
            self.char = '✔'
            self.pad = 2
            info_len = self.bar_len + self.max_att + len(_('palabras')) \
                + 10 + self.pad * 2

            self.textS = tk.Text(self.window)
            self.textS['font'] = 'mono 10'
            self.textS['relief'] = 'flat'
            self.textS['width'] = info_len
            self.textS['height'] = len(self.sessions) + 2
            self.textS.tag_configure('guess', foreground='green')
            self.textS.tag_configure('wrong', foreground='white')
            self.textS.pack(fill='x', expand='yes')
            self.textS.insert('1.0', '\n')

            line = 2
            for session in self.sessions:
                self.percentbar(session, line)
                line += 1

    def percentbar(self, session, line):
        attempts = session.attempts
        percent = session.percent
        sep = int(self.bar_len * session.percent / 100)
        perc_str = str(percent).rjust(3) + '%'
        atte_str = str(attempts).rjust(self.max_att)

        template = '{}{} {} {} {} {}{}\n'
        info = template.format(self.pad * ' ', self.char * self.bar_len,
                               perc_str, _('de'), atte_str, _('palabras'),
                               self.pad * ' ')

        self.textS['state'] = 'normal'

        self.textS.insert('{}.{}'.format(line, self.pad), info)
        # guess
        start = '{}.{}'.format(line, self.bar_len - sep + self.pad)
        end = '{}.{}'.format(line, self.bar_len + self.pad)
        self.textS.tag_add('guess', start, end)
        # wrong
        start = '{}.{}'.format(line, self.pad)
        end = '{}.{}'.format(line, self.bar_len - sep + self.pad)
        self.textS.tag_add('wrong', start, end)

        self.textS['state'] = 'disabled'

    def destroyWin(self, event=None):
        self.window.destroy()


def main():
    pass


if __name__ == '__main__':
    main()
