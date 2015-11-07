#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Script Name:          vocapy.py
# Author:               Alejandro Druetta
# Version:              0.3
#
# Description:          Aplicación para el aprendizaje de vocabulario de
#                       lenguas extranjeras.

import time
import gettext
import locale
import tkinter as tk
import webbrowser
from tkinter import messagebox
from classes import WordList, PercentBar, Session, PracticeRound, ConfDict
from classes import DEBUG
from constructor import ConstList


class VocapyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window geometry
        self.title('VocaPy')
        self.resizable(0, 0)
        self.padding = 20

        # General settings
        self.version = '0.3'
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
        self.bind('<Control-a>', self.constructorCall)
        self.bind('<Control-e>', self.statsCall)
        self.urlHelp = 'https://github.com/aledruetta/vocapy'
        self.bind_all('<F1>', lambda e: self.openUrl(self.urlHelp))

        # Configurations
        self.cf_dict = ConfDict()
        self.cf_dict.load()
        self.lang = self.cf_dict.setdefault('lang', locale.getlocale()[0])

        # Localization
        self.i18n()

        # Game
        self.minWords = 5
        self.session = Session(time.time(), attempts=0, guess=0)
        self.word_list = WordList()
        self.main_window()
        self.practice()

    def main_window(self):

        # Menu
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
        self.buttonF['command'] = self.practice
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

    def practice(self, event=None):
        while len(self.word_list) < self.minWords:
            self.list_complete()

        # Practice round
        self.gr = PracticeRound(self.word_list)

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

        # New practice round
        self.buttonF['state'] = 'normal'
        self.buttonF.bind('<Return>', self.practice)
        self.buttonF.focus_set()

    def show_result(self, success):
        title = _('Resultado')
        padl = 4 * ' '
        padr = 12 * ' '

        # Messagebox
        if success:
            message = _('\n{}Resultado: Correcto!{}').format(padl, padr)
            messagebox.showinfo(title, message, parent=self)
        else:
            message = _('{0}Resultado: Incorrecto!{1}\n{0}{2}: {3}{1}').format(
                padl, padr, self.gr.word.name, self.gr.target)
            messagebox.showerror(title, message, parent=self)

    def list_complete(self):
        # Messagebox
        message = _('''El diccionario posee {} términos.
Antes de jugar debería añadir al menos {} términos al diccionario.
''').format(len(self.word_list), self.minWords - len(self.word_list))
        messagebox.showinfo(_('Advertencia'), message, parent=self)

        self.constructorCall()

    def percentbar(self):
        attempts = self.session.attempts
        percent = self.session.percent

        start = len(str(attempts)) + len(_('palabras')) + 2
        info = _('{} palabras  [{}{} aciertos]').format(attempts, percent, '%')

        self.textS['state'] = 'normal'
        self.textS.delete('1.0', tk.END)
        self.textS.insert('1.0', info)

        pBar = PercentBar(
            self.textS,
            start=(1, start),
            lenght=30,
            char=' ',
            percent=percent,
            colors=('#CBE148', '#EEB0AB')
            )
        pBar.create()

        self.textS['state'] = 'disabled'

    def constructorCall(self, event=None):
        self.unbind('<Control-a>')
        constructor = ConstList(self)
        constructor.wait_window()
        self.word_list = constructor.word_list
        self.bind('<Control-a>', self.constructorCall)

    def statsCall(self, event=None):
        self.unbind('<Control-e>')
        statistics = Statistics(self)
        statistics.wait_window()
        self.bind('<Control-e>', self.statsCall)

    def menuBar(self):
        menuBar = tk.Menu(self)
        self.config(menu=menuBar)

        # Archivo
        fileMenu = tk.Menu(menuBar, tearoff=0)
        fileMenu.add_command(
            label=_('Agregar palabras'),
            accelerator='Ctrl+A',
            command=self.constructorCall
            )
        fileMenu.add_command(
            label=_('Eliminar palabra'),
            accelerator='Ctrl+D',
            command=self.delWord
            )
        self.bind('<Control-d>', self.delWord)
        fileMenu.add_command(
            label=_('Borrar todo'),
            command=self.clear
            )
        fileMenu.add_separator()

        langMenu = tk.Menu(fileMenu, tearoff=0)        # Language
        fileMenu.add_cascade(label=_('Lenguaje'), menu=langMenu)
        langs_lst = [_('español'), _('portugués'), _('inglés')]
        for l in langs_lst:
            langMenu.add_radiobutton(label=l, indicatoron=0,
                                     command=lambda arg0=l: self.setLang(arg0)
                                     )

        fileMenu.add_separator()
        fileMenu.add_command(
            label=_('Ver estadísticas'),
            accelerator='Ctrl+E',
            command=self.statsCall
            )
        fileMenu.add_separator()
        fileMenu.add_command(
            label=_('Salir'),
            accelerator='Ctrl+Q',
            command=self.destroyWin
            )
        menuBar.add_cascade(label=_('Archivo'), menu=fileMenu)

        # Ayuda
        helpMenu = tk.Menu(menuBar, tearoff=0)
        helpMenu.add_command(
            label=_('Ayuda'),
            accelerator='F1',
            command=lambda: self.openUrl(self.urlHelp)
            )
        helpMenu.add_command(label=_('Sobre'), command=self.about)
        menuBar.add_cascade(label=_('Ayuda'), menu=helpMenu)

    def openUrl(self, url, event=None):
        webbrowser.open(url)

    def about(self):
        """About messagebox"""

        title = _('Sobre')
        message = """
                    VocaPy
                      v{}

              MIT License (MIT)
Copyright (c) 2014 Alejandro Druetta\t
 https://github.com/aledruetta/vocapy
    """.format(self.version)
        messagebox.showinfo(title, message, parent=self)

    def setLang(self, arg0):
        if arg0 == _('español'):
            self.lang = 'es_AR'
        elif arg0 == _('portugués'):
            self.lang = 'pt_BR'
        elif arg0 == _('inglés'):
            self.lang = 'en_US'

        self.cf_dict.save('lang', self.lang)
        self.i18n()
        self.menuBar()
        self.percentbar()

        if DEBUG:
            print('\nmenu: {}\n'.format(self.lang))

    def delWord(self, event=None):
        m = _('Está seguro de que quiere eliminar {} del diccionario?').format(
            self.gr.word.name)
        t = _('Eliminar Palabra')
        if messagebox.askokcancel(t, m, default='cancel', parent=self):
            self.word_list.remove_db(self.gr.word)
            if DEBUG:
                print("\n", self.word_list)

        self.practice()

    def clear(self):
        m = _('Está seguro de que quiere eliminar el diccionario?')
        t = _('Eliminar Diccionario')
        if messagebox.askokcancel(t, m, default='cancel', parent=self):
            self.word_list.clear()

        self.practice()

    def destroyWin(self, event=None):
        self.session.append_db()
        if DEBUG:
            print("\n{}\n".format(self.session.sessions_lst))
        self.destroy()

    def i18n(self):
        """
        Localization:
            1. 'string' to _('string')
            2. File's list to potfiles.in
            3. To create .pot file:
                $ xgettext --files-from=potfiles.in --directory=../.. \
                    --output=messages.pot --language=Python --from-code=utf-8
            4. Edit message.pot with poedit
            5. Put in locale/lang/LC_MESSAGES/
            6. To update:
                $ msgmerge --update --no-fuzzy-matching --buckup=off \
                    ../../locale/lang/LC_MESSAGES/messages.po messages.pot
                Edit message.po with poedit
        """

        try:
            lang = gettext.translation('messages', localedir='locale',
                                       languages=[self.lang])
        except (OSError, AttributeError) as err:
            lang = gettext.NullTranslations()
            if DEBUG:
                print("\nError: {}".format(err))
        lang.install()


class Statistics(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title(_('Estadísticas'))
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
