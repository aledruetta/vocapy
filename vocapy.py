#! /usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
from copy import copy
import time
import classes
import random
import sys

class VocapyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('VocaPy')
        self.resizable(0, 0)
        self.padding = 20

        self.path = 'dict.txt'
        self.pathsessions = 'sessions.txt'
        self.dictionary = classes.load_dict(self.path)

        self.option_add('*font', 'helvetica 11')
        self.option_add('*Entry.font', 'helvetica 12')
        self.option_add('*Listbox.font', 'helvetica 12')
        self.option_add('*Menu.background', 'snow')
        self.option_add('*Text.background', 'snow')
        self.option_add('*Menu.relief', 'flat')
        self.option_add('*Text.relief', 'flat')

        self.protocol("WM_DELETE_WINDOW", self.destroyWin)
        self.bind('<Control-q>', self.destroyWin)
        self.bind('<Control-a>', self.constructorcall)
        self.bind('<Control-e>', self.statscall)
        self.bind_all('<F1>', self.helpWin)

        self.session = classes.Session()

        self.session['time']    = time.time()
        self.session['display'] = 0
        self.session['guess']   = 0

        self.interface()

        while len(self.dictionary) < 4:
            self.dictcomplete()

        self.ranking()
        self.play()

    def interface(self):

        color = 'crimson'

        self.menuBar()

        labelFrameApp = tk.LabelFrame(self)
        labelFrameApp['bg'] = color
        labelFrameApp.pack(fill='x', expand='yes')

        self.labelW = tk.Label(labelFrameApp)
        self.labelW['font'] = ('Arial Black', 36)
        self.labelW['bg'] = color
        self.labelW['fg'] = 'snow'
        self.labelW['text'] = 'VOCAPY'
        self.labelW.pack(padx=self.padding, pady=self.padding)

        frameB = tk.Frame(labelFrameApp)
        frameB['bg'] = color
        frameB.pack(padx=self.padding)

        self.radiobuttons = []
        for i in range(4):
            self.radiobuttons.append(tk.Radiobutton(frameB))
            self.radiobuttons[i]['indicatoron'] = 0
            self.radiobuttons[i]['font']   = 'helvetica 16 bold'
            self.radiobuttons[i]['height'] = 2
            self.radiobuttons[i]['width']  = 40
            self.radiobuttons[i]['bg']     = 'Teal'
            self.radiobuttons[i]['fg']     = 'snow'
            self.radiobuttons[i].pack(fill ='x', expand='yes', pady=3)

        self.radiobuttons[0]['command'] = lambda: self.check_guess(self.radiobuttons[0])
        self.radiobuttons[1]['command'] = lambda: self.check_guess(self.radiobuttons[1])
        self.radiobuttons[2]['command'] = lambda: self.check_guess(self.radiobuttons[2])
        self.radiobuttons[3]['command'] = lambda: self.check_guess(self.radiobuttons[3])

        self.buttonF = tk.Button(labelFrameApp)
        self.buttonF['command'] = self.play
        self.buttonF['text']    = '-->'
        self.buttonF['font']    = ('Arial Black', 20, 'bold')
        self.buttonF['bg']      = 'snow'
        self.buttonF['fg']      = 'Teal'
        self.buttonF.pack(padx=self.padding, pady=self.padding, ipadx=10, ipady=5)

        self.textS = tk.Text(self)
        self.textS['font']   = 'helvetica 10'
        self.textS['relief'] = 'flat'
        self.textS['height'] = 1
        self.textS.tag_configure('guess', background='#CBE148')
        self.textS.tag_configure('wrong', background='#EEB0AB')
        self.textS.pack(fill='x', expand='yes')

        self.percentbar()

    def play(self, event=None):

        try:
            self.word = self.ranking_list.pop(0)
        except IndexError:
            self.newsession()
        
        self.labelW['text'] = self.word            

        self.buttonF['state'] = 'disabled'
        self.buttonF.unbind('<Return>')

        self.user_guess = tk.StringVar()
        self.choice_list()

        for i in range(4):
            self.radiobuttons[i]['variable'] = self.user_guess
            self.radiobuttons[i]['text']     = self.choices[i]
            self.radiobuttons[i]['value']    = self.choices[i]
            self.radiobuttons[i]['state']    = 'normal'

        self.focus_set()

    def percentbar(self):

        display = self.session['display']
        
        self.session.percent()
        percent = self.session['percent']
        
        start = len(str(display)) + 10
        info = '{} palabras  [{}{} aciertos]'.format(display, percent, '%')

        self.textS['state'] = 'normal'
        self.textS.delete('1.0', tk.END)
        self.textS.insert('1.0', info)

        percentbar = classes.PercentBar(
            self.textS, 
            start=(1, start), 
            lenght=30, 
            char=' ', 
            percent=percent, 
            colors=('#CBE148', '#EEB0AB')
            )
        percentbar.create()

        self.textS['state'] = 'disabled'

    def check_guess(self, button):

        guess = self.user_guess.get()

        if guess == self.target:
            button['selectcolor'] = '#CBE148'
            self.dictionary[self.word].grow_guess()
            self.session['guess'] += 1
            result = True
        else:
            button['selectcolor'] = '#EEB0AB'
            result = False

        lasttime = time.time()

        self.dictionary[self.word].grow_display()
        self.session['display'] += 1
        self.dictionary[self.word].time = lasttime

        classes.save_dict(self.dictionary, self.path)

        self.show_result(result)
        self.percentbar()

        for i in range(4):
            self.radiobuttons[i]['state'] = 'disabled'

        self.buttonF['state'] = 'normal'
        self.buttonF.bind('<Return>', self.play)
        self.buttonF.focus_set()

    def ranking(self):

        self.ranking_list = copy(list(self.dictionary.keys()))
        
        count = 1
        length = len(self.ranking_list)

        while count < length:
            for i in range(length-count):
                aper = self.dictionary[self.ranking_list[i]].percent_guess()
                bper = self.dictionary[self.ranking_list[i+1]].percent_guess()

                atim = self.dictionary[self.ranking_list[i]].time
                btim = self.dictionary[self.ranking_list[i+1]].time

                if atim > btim or (atim == btim and aper > bper):
                    temp_key = self.ranking_list[i]
                    self.ranking_list[i] = self.ranking_list[i+1]
                    self.ranking_list[i+1] = temp_key

            count += 1

    def choice_list(self):
       
        random_keys = copy(self.dictionary.random_keys())

        while len(random_keys) < 4:
            self.dictcomplete()
            random_keys = copy(self.dictionary.random_keys())

        random_keys.remove(self.word)

        self.choices = list()
        count = 0
        while count < 3:
            random_key = random_keys.pop()
            mean = self.dictionary[random_key].random_mean()
            if mean not in self.choices:
                self.choices.append(mean)
                count += 1

        self.target = self.dictionary[self.word].random_mean()
        self.choices.append(self.target)
        random.shuffle(self.choices)

    def show_result(self, success):

        title = 'Resultado'
        padl = 4 * ' '
        padr = 12 * ' '

        if success:
            message = '\n{}Resultado: Correcto!{}'.format(padl, padr)
            messagebox.showinfo(title, message)
        else:
            message = '{0}Resultado: Incorrecto!{1}\n{0}{2}: {3}{1}'.format(padl, \
                padr, self.word, self.target)
            messagebox.showerror(title, message)

    def dictcomplete(self):

        message = '''El diccionario posee {} términos. 
Antes de jugar debería añadir al menos {} términos al diccionario.
'''.format(self.dictionary.count_keys(), 4 - self.dictionary.count_keys())

        messagebox.showinfo('Advertencia', message)

        self.constructorcall()

    def newsession(self):

        m = 'No hay más palabras para practicar.\nQuiere comenzar de nuevo?'
        t = 'Diccionario Fin'

        if messagebox.askyesno(t, m, default='no'):
            self.ranking()
            self.play()
        else:
            self.destroyWin()

    def constructorcall(self, event=None):

        self.unbind('<Control-a>')
        constructor = ConstDict(self)
        constructor.wait_window()
        self.dictionary = constructor.dictionary
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
            label='Limpiar diccionario', 
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
        menubar.add_cascade(label='Archivo', menu= filemenu )

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

        m = 'Está seguro de que quiere eliminar {} del diccionario?'.format(self.word)
        t = 'Eliminar Palabra'

        if messagebox.askokcancel(t, m, default='cancel'):
            self.dictionary.pop(self.word)
            classes.save_dict(self.dictionary, self.path)
            self.play()

    def clear(self):

        m = 'Está seguro de que quiere eliminar el diccionario?'
        t = 'Eliminar Diccionario'

        if messagebox.askokcancel(t, m, default='cancel'):
            self.dictionary.clear()
            classes.save_dict(self.dictionary, self.path)
            self.play()

    def destroyWin(self, event=None):

        self.savesession()
        self.destroy()

    def savesession(self):

        if self.session['display'] > 0:

            sessions_lst = classes.load_sessions(self.pathsessions)            
        
            if len(sessions_lst) > 0:

                current = time.localtime(self.session['time'])[:3]
                last    = time.localtime(sessions_lst[-1][0])[:3]

                if current == last:
                    self.session['display'] += sessions_lst[-1][1]
                    self.session['guess']   += sessions_lst[-1][2]
                    sessions_lst.pop()
            
            self.session.percent()

            list_write = [[
                self.session['time'],
                self.session['display'],
                self.session['guess'],
                self.session['percent']
                ]]

            sessions_lst.extend(list_write)

            classes.save_csvfile(sessions_lst, self.pathsessions)

    def helpWin(self, event=None):
        print('help')






class ConstDict(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title('Constructor')
        self.resizable(0, 0)
        self.padding = 20

        self.bind('<Control-q>', self.destroyWin)

        self.path = 'dict.txt'
        self.dictionary = classes.load_dict(self.path)

        self.entryWord()
        self.entryMeans()
        self.clear()

    def destroyWin(self, event):
        self.destroy()        

    def entryWord(self):

        labelframeW = tk.LabelFrame(self)
        labelframeW.grid(row=0, column=0, sticky='ew')

        frameW = tk.Frame(labelframeW)
        frameW.pack(fill='x', expand='yes', padx=self.padding, pady=self.padding)

        labelW = tk.Label(frameW)
        labelW['text'] = 'Palabra:'
        labelW.pack(side='left')

        self.entryW = tk.Entry(frameW)
        self.entryW.pack(side='left', fill='x', expand='yes', padx=self.padding/2, ipady=2)

        self.buttonW = tk.Button(frameW)
        self.buttonW['text']    = '+'
        self.buttonW.pack(side='left')

    def entryMeans(self):

        labelframeM = tk.LabelFrame(self)
        labelframeM.grid(row=1, column=0)

        frameM1 = tk.Frame(labelframeM)
        frameM1.grid(row=0, column=0, sticky='nw', padx=self.padding, pady=self.padding)

        labelM = tk.Label(frameM1)
        labelM['text'] = 'Significado:'
        labelM.pack(side='left')

        self.entryM = tk.Entry(frameM1)
        self.entryM['width'] = 20
        self.entryM.bind('<Return>', self.addmean)
        self.entryM.pack(side='left', ipady=2, padx=self.padding/2)

        self.buttonM = tk.Button(frameM1)
        self.buttonM['text']    = '+'
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
        frameF.pack(fill='x', expand='yes', padx=self.padding, pady=self.padding)

        self.labelF = tk.Label(frameF)
        self.labelF['font'] = 'Arial 9 italic'
        lenght = len(self.dictionary.keys())
        self.labelF['text'] = str(lenght) + ' palabras'
        self.labelF.pack(side='left')

        self.buttonA = tk.Button(frameF)
        self.buttonA['text']    = 'Avanzar'
        self.buttonA['command'] = self.forward
        self.buttonA['width']   = 8
        self.buttonA.pack(side='right')

        self.buttonL = tk.Button(frameF)
        self.buttonL['text']    = 'Limpiar'
        self.buttonL['command'] = self.clear
        self.buttonL['width']   = 8
        self.buttonL.pack(side='right')

    def addname(self, event=None):
        
        if self.entryW.get() != '':
            self.entryW.unbind('<Return>')
            self.buttonW.deletecommand(str(self.buttonW.cget('command')))

            self.entryW['fg'] = 'red'
            self.word.name = self.entryW.get().upper()
            self.entryW.delete(0, tk.END)
            self.entryW.insert(0, self.word.name)
            self.entryW['state'] = 'readonly'

            self.entryM['state'] = 'normal'
            self.entryM.focus_set()
            self.buttonM['state'] = 'normal'

    def addmean(self, event=None):
        mean = self.entryM.get().lower()
        if mean != '':
            self.word.add(mean)
            self.listboxM.insert(0, ' {}'.format(mean))
            self.entryM.delete(0, tk.END)
            self.buttonA['state'] = 'normal'

    def clear(self):
        self.entryW.focus_set()
        self.entryW.bind('<Return>', self.addname)
        self.entryW['state'] = 'normal'
        self.entryW.delete(0, tk.END)
        self.entryW['fg']    = 'black'

        self.buttonW['command'] = self.addname

        self.entryM['state'] = 'disabled'
        self.entryM.delete(0, tk.END)
        self.buttonM['state'] = 'disabled'

        self.listboxM.delete(0, tk.END)

        self.buttonA['state'] = 'disabled'

        self.word = classes.VocapySet(None)

    def forward(self):
        
        self.dictionary[self.word.name] = self.word
        classes.save_dict(self.dictionary, self.path)
        lenght = len(self.dictionary.keys())
        self.labelF['text'] = str(lenght) + ' palabras'

        self.clear()




        

class Statistics(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
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