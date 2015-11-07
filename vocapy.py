#! /usr/bin/env python3

# Script Name:          vocapy.py
# Author:               Alejandro Druetta
# Version:              0.2
#
# Description:          Aplicación para el aprendizaje de vocabulario de
#                       lenguas extranjeras.

import time
import tkinter as tk
from tkinter import messagebox
from classes import WordList, PercentBar, Session, GameRound
from constructor import ConstList

DEBUG = True
MINWORDS = 5


class VocapyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window geometry
        self.title('VocaPy')
        self.resizable(0, 0)
        self.padding = 20

        # General settings
        self.option_add('*font', 'helvetica 11')
        self.option_add('*Entry.font', 'helvetica 12')
        self.option_add('*Listbox.font', 'helvetica 12')
        self.option_add('*Menu.background', 'snow')
        self.option_add('*Text.background', 'snow')
        self.option_add('*Menu.relief', 'flat')
        self.option_add('*Text.relief', 'flat')

        # Shortcuts
        self.protocol("WM_DELETE_WINDOW", self.destroyWin)
        self.bind('<Control-q>', self.destroyWin)
        self.bind('<Control-a>', self.constructorcall)
        self.bind('<Control-e>', self.statscall)
        self.bind_all('<F1>', self.helpWin)

        self.session = Session(time.time(), attempts=0, guess=0)
        self.word_list = WordList()
        self.main_window()
        self.play_game()

    def main_window(self):
        self.menuBar()

        # Background
        color = 'crimson'
        labelFrameApp = tk.LabelFrame(self)
        labelFrameApp['bg'] = color
        labelFrameApp.pack(fill='x', expand='yes')

        # Word label
        self.labelW = tk.Label(labelFrameApp)
        self.labelW['font'] = ('Arial Black', 36)
        self.labelW['bg'] = color
        self.labelW['fg'] = 'snow'
        self.labelW['text'] = 'VOCAPY'
        self.labelW.pack(padx=self.padding, pady=self.padding)

        # Frame choice buttons
        frameB = tk.Frame(labelFrameApp)
        frameB['bg'] = color
        frameB.pack(padx=self.padding)

        # Choice buttons create
        self.radiobuttons = []
        for i in range(4):
            self.radiobuttons.append(tk.Radiobutton(frameB))
            self.radiobuttons[i]['indicatoron'] = 0
            self.radiobuttons[i]['font'] = 'helvetica 16 bold'
            self.radiobuttons[i]['height'] = 2
            self.radiobuttons[i]['width'] = 40
            self.radiobuttons[i]['bg'] = 'Teal'
            self.radiobuttons[i]['fg'] = 'snow'
            self.radiobuttons[i].pack(fill='x', expand='yes', pady=3)

        # Choice buttons commands
        self.radiobuttons[0]['command'] = lambda: self.check_guess(
            self.radiobuttons[0])
        self.radiobuttons[1]['command'] = lambda: self.check_guess(
            self.radiobuttons[1])
        self.radiobuttons[2]['command'] = lambda: self.check_guess(
            self.radiobuttons[2])
        self.radiobuttons[3]['command'] = lambda: self.check_guess(
            self.radiobuttons[3])

        # Next word button
        self.buttonF = tk.Button(labelFrameApp)
        self.buttonF['command'] = self.play_game
        self.buttonF['text'] = '-->'
        self.buttonF['font'] = ('Arial Black', 20, 'bold')
        self.buttonF['bg'] = 'snow'
        self.buttonF['fg'] = 'Teal'
        self.buttonF.pack(
            padx=self.padding,
            pady=self.padding,
            ipadx=10,
            ipady=5
        )

        # Percentbar
        self.textS = tk.Text(self)
        self.textS['font'] = 'helvetica 10'
        self.textS['relief'] = 'flat'
        self.textS['height'] = 1
        self.textS.tag_configure('guess', background='#CBE148')
        self.textS.tag_configure('wrong', background='#EEB0AB')
        self.textS.pack(fill='x', expand='yes')

        self.percentbar()

    def play_game(self, event=None):
        while len(self.word_list) < MINWORDS:
            self.list_complete()

        # Game round
        self.gr = GameRound(self.word_list)

        if DEBUG:
            print(self.gr)

        # Display word
        self.labelW['text'] = self.gr.word.name

        self.buttonF['state'] = 'disabled'
        self.buttonF.unbind('<Return>')

        self.user_guess = tk.StringVar()

        # Display choices
        for i in range(4):
            self.radiobuttons[i]['variable'] = self.user_guess
            self.radiobuttons[i]['text'] = self.gr.means[i]
            self.radiobuttons[i]['value'] = self.gr.means[i]
            self.radiobuttons[i]['state'] = 'normal'

        self.focus_set()

    def check_guess(self, button):
        # Update attempts
        self.gr.word.attempts += 1
        self.session.attempts += 1

        # User choice
        guess = self.user_guess.get()
        if guess == self.gr.target:
            button['selectcolor'] = '#CBE148'
            # Update guess
            self.gr.word.guess += 1
            self.session.guess += 1
            result = True
        else:
            button['selectcolor'] = '#EEB0AB'
            result = False

        self.gr.word.update_db()
        self.show_result(result)
        self.percentbar()

        for i in range(4):
            self.radiobuttons[i]['state'] = 'disabled'

        # New round game
        self.buttonF['state'] = 'normal'
        self.buttonF.bind('<Return>', self.play_game)
        self.buttonF.focus_set()

    def show_result(self, success):
        title = 'Resultado'
        padl = 4 * ' '
        padr = 12 * ' '

        # Messagebox
        if success:
            message = '\n{}Resultado: Correcto!{}'.format(padl, padr)
            messagebox.showinfo(title, message)
        else:
            message = '{0}Resultado: Incorrecto!{1}\n{0}{2}: {3}{1}'.format(
                padl, padr, self.gr.word.name, self.gr.target)
            messagebox.showerror(title, message)

    def list_complete(self):
        # Messagebox
        message = '''El diccionario posee {} términos.
Antes de jugar debería añadir al menos {} términos al diccionario.
'''.format(len(self.word_list), MINWORDS - len(self.word_list))
        messagebox.showinfo('Advertencia', message)

        self.constructorcall()

    def percentbar(self):
        attempts = self.session.attempts
        percent = self.session.percent

        start = len(str(attempts)) + 10
        info = '{} palabras  [{}{} aciertos]'.format(attempts, percent, '%')

        self.textS['state'] = 'normal'
        self.textS.delete('1.0', tk.END)
        self.textS.insert('1.0', info)

        percentbar = PercentBar(
            self.textS,
            start=(1, start),
            lenght=30,
            char=' ',
            percent=percent,
            colors=('#CBE148', '#EEB0AB')
            )
        percentbar.create()

        self.textS['state'] = 'disabled'

    def constructorcall(self, event=None):
        self.unbind('<Control-a>')
        constructor = ConstList(self)
        constructor.wait_window()
        self.word_list = constructor.word_list
        self.bind('<Control-a>', self.constructorcall)

    def statscall(self, event=None):
        self.unbind('<Control-e>')
        statistics = Statistics(self)
        statistics.wait_window()
        self.bind('<Control-e>', self.statscall)

    def menuBar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Archivo
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label='Agregar palabras',
            accelerator='Ctrl+A',
            command=self.constructorcall
            )
        filemenu.add_command(
            label='Eliminar palabra',
            accelerator='Ctrl+D',
            command=self.delword
            )
        self.bind('<Control-d>', self.delword)
        filemenu.add_command(
            label='Borrar todo',
            command=self.clear
            )
        filemenu.add_separator()
        filemenu.add_command(
            label='Ver estadísticas',
            accelerator='Ctrl+E',
            command=self.statscall
            )
        filemenu.add_separator()
        filemenu.add_command(
            label='Salir',
            accelerator='Ctrl+Q',
            command=self.destroyWin
            )
        menubar.add_cascade(label='Archivo', menu=filemenu)

        # Ayuda
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(
            label='Ayuda',
            accelerator='F1',
            command=self.helpWin
            )
        helpmenu.add_command(label='Sobre')
        menubar.add_cascade(label='Ayuda', menu=helpmenu)

    def delword(self, event=None):
        m = 'Está seguro de que quiere eliminar {} del diccionario?'.format(
            self.gr.word.name)
        t = 'Eliminar Palabra'
        if messagebox.askokcancel(t, m, default='cancel'):
            self.word_list.remove_db(self.gr.word)

        self.play_game()

    def clear(self):
        m = 'Está seguro de que quiere eliminar el diccionario?'
        t = 'Eliminar Diccionario'
        if messagebox.askokcancel(t, m, default='cancel'):
            self.word_list.clear()

        self.play_game()

    def destroyWin(self, event=None):
        self.session.append_db()
        if DEBUG:
            print(self.session.sessions_lst)
        self.destroy()

    def helpWin(self, event=None):
        if DEBUG:
            print('help')


class Statistics(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Estadísticas')
        self.resizable(0, 0)

        self.bind('<Control-q>', self.destroyWin)

        text = tk.Text(self)
        text.pack()

    def destroyWin(self, event=None):
        self.destroy()


def main():
    root = VocapyApp()
    root.mainloop()

if __name__ == '__main__':
    main()
