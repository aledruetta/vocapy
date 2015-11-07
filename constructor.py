#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Script Name:          constructor.py
# Author:               Alejandro Druetta
# Version:              0.3
#
# Description:          Aplicación para el aprendizaje de vocabulario de
#                       lenguas extranjeras.

import tkinter as tk
import sqlite3 as sql
from tkinter import messagebox
from classes import VocapyWord
from classes import DEBUG


class ConstList(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.word_list = master.word_list

        # Window geometry
        self.title(_('Constructor'))
        self.resizable(0, 0)
        self.padding = 20

        self.bind('<Control-q>', self.destroyWin)

        # Interface
        self.entryWord()
        self.entryMeans()
        self.clear()

    def destroyWin(self, event):
        self.destroy()

    def entryWord(self):
        labelframeW = tk.LabelFrame(self)
        labelframeW.grid(row=0, column=0, sticky='ew')

        frameW = tk.Frame(labelframeW)
        frameW.pack(fill='x', expand='yes', padx=self.padding,
                    pady=self.padding)

        labelW = tk.Label(frameW)
        labelW['text'] = _('Palabra:')
        labelW.pack(side='left')

        self.entryW = tk.Entry(frameW)
        self.entryW.pack(side='left', fill='x', expand='yes',
                         padx=self.padding/2, ipady=2)

        self.buttonW = tk.Button(frameW)
        self.buttonW['text'] = '+'
        self.buttonW.pack(side='left')

    def entryMeans(self):
        labelframeM = tk.LabelFrame(self)
        labelframeM.grid(row=1, column=0)

        frameM1 = tk.Frame(labelframeM)
        frameM1.grid(row=0, column=0, sticky='nw', padx=self.padding,
                     pady=self.padding)

        labelM = tk.Label(frameM1)
        labelM['text'] = _('Significado:')
        labelM.pack(side='left')

        self.entryM = tk.Entry(frameM1)
        self.entryM['width'] = 20
        self.entryM.bind('<Return>', self.addmean)
        self.entryM.pack(side='left', ipady=2, padx=self.padding/2)

        self.buttonM = tk.Button(frameM1)
        self.buttonM['text'] = '+'
        self.buttonM['command'] = self.addmean
        self.buttonM.pack(side='left')

        frameM2 = tk.Frame(labelframeM)
        frameM2.grid(row=0, column=1)

        self.listboxM = tk.Listbox(frameM2)
        self.listboxM['width'] = 20
        self.listboxM.pack()

        labelframeF = tk.LabelFrame(self)
        labelframeF.grid(row=2, column=0, sticky='ew')

        frameF = tk.Frame(labelframeF)
        frameF.pack(fill='x', expand='yes', padx=self.padding,
                    pady=self.padding)

        self.labelF = tk.Label(frameF)
        self.labelF['font'] = 'Arial 9 italic'
        lenght = len(self.word_list)
        self.labelF['text'] = str(lenght) + _(' palabras')
        self.labelF.pack(side='left')

        self.buttonA = tk.Button(frameF)
        self.buttonA['text'] = _('Avanzar')
        self.buttonA['command'] = self.forward
        self.buttonA['width'] = 8
        self.buttonA.pack(side='right')

        self.buttonL = tk.Button(frameF)
        self.buttonL['text'] = _('Limpiar')
        self.buttonL['command'] = self.clear
        self.buttonL['width'] = 8
        self.buttonL.pack(side='right')

    def addname(self, event=None):
        entry_get = self.entryW.get().upper()
        if entry_get:
            self.entryW.unbind('<Return>')
            self.buttonW.deletecommand(str(self.buttonW.cget('command')))

            self.entryW['fg'] = 'red'
            self.word.name = entry_get
            self.entryW.delete(0, tk.END)
            self.entryW.insert(0, self.word.name)
            self.entryW['state'] = 'readonly'

            self.entryM['state'] = 'normal'
            self.entryM.focus_set()
            self.buttonM['state'] = 'normal'

    def addmean(self, event=None):
        mean = self.entryM.get().lower()
        if mean:
            self.word.means.append(mean)
            self.listboxM.insert(0, ' {}'.format(mean))
            self.entryM.delete(0, tk.END)
            self.buttonA['state'] = 'normal'

    def clear(self):
        self.entryW.focus_set()
        self.entryW.bind('<Return>', self.addname)
        self.entryW['state'] = 'normal'
        self.entryW.delete(0, tk.END)
        self.entryW['fg'] = 'black'

        self.buttonW['command'] = self.addname

        self.entryM['state'] = 'disabled'
        self.entryM.delete(0, tk.END)
        self.buttonM['state'] = 'disabled'

        self.listboxM.delete(0, tk.END)

        self.buttonA['state'] = 'disabled'

        # Empty word for constructor
        self.word = VocapyWord(None, 0.0, 0, 0, list())

    def forward(self):
        try:
            self.word_list.append_db(self.word)
        except sql.IntegrityError:
            message = _('No es posible adicionar palabras o significados \
repetidos a la base de datos.')
            messagebox.showinfo(_('Advertencia'), message, parent=self)

        lenght = len(self.word_list)
        self.labelF['text'] = str(lenght) + _(' palabras')

        self.clear()

        if DEBUG:
            print("\n", self.word_list)


def main():
    pass

if __name__ == '__main__':
    main()
