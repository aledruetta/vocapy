#!/usr/bin/env python3

import csv
import sys
import random
from copy import copy
import time


class VocapySet(set):

	def __init__(self, word, display=0, guess=0, time=0):
		set.__init__(set())
		self.name = word
		self.display = display
		self.guess = guess
		self.time = time

	def random_mean(self):
		random_list = self.means_sorted_list()
		random.shuffle(random_list)
		return random_list[0]

	def count_means(self):
		return self.__len__()

	def means_sorted_list(self):
		return sorted(list(self)) 

	def grow_display(self):
		self.display += 1

	def grow_guess(self):
		self.guess += 1

	def percent_guess(self):
		try:
			return int((self.guess * 100) / self.display)
		except ZeroDivisionError:
			return 0


class VocapyDict(dict):

	def __init__(self, word_lang="inglés", mean_lang="español"):
		dict.__init__(dict())
		self.word_lang = word_lang
		self.mean_lang = mean_lang

	def append(self, word):
		if word.name not in self.keys():
			self[word.name] = word
			return False
		else:
			self[word.name].update(word)
			return True

	def random_keys(self):
		random_list = copy(self.keys_sorted_list())
		random.shuffle(random_list)
		return random_list

	def count_keys(self):
		return self.__len__()

	def keys_sorted_list(self):
		return sorted(list(self.keys()))


class VocapyStats(dict):
	def __init__(self):
		dict.__init__(self, dict())

	def keys_sorted_list(self):
		return sorted(list(self.keys()))

	def percent_sorted_list(self):
		return self.bubble(1)

	def display_sorted_list(self):
		return self.bubble(0)

	def time_sorted_list(self):
		return self.bubble(2)

	def bubble(self, index):
		count = 1
		key_list = list(self.keys())
		lenght = len(key_list)

		while count < lenght:
			for i in range(lenght-count):
				a = self[key_list[i]][index]
				b = self[key_list[i+1]][index]
				if a > b:
					temp = key_list.pop(i)
					key_list.insert(i+1, temp)
			count += 1

		return key_list


class Session(dict):
	def __init__(self):
		dict.__init__(self)

	def percent(self):
		try:
			self['percent'] = round(100 * self['guess'] / self['display'])
		except ZeroDivisionError:
			self['percent'] = 0


class PercentBar:
	def __init__(self, text, start, lenght, char, percent, colors):
		self.text = text		# Object tk.Text
		self.start = start 		# Coords Tuple, ex: (1, 0)
		self.lenght = lenght
		self.char = char
		self.percent = percent
		self.colors = colors	# Colors Tuple, ex: ('green', 'red')

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



def strtotuple(string):
        
        string = string.strip('(').strip(')')
        lst = string.split(', ')

        for i in range(len(lst)):
            lst[i] = int(lst[i])

        tup = tuple(lst)

        return tup

def load_dict(path):

	dictionary = VocapyDict()
	list_read  = load_csvfile(path)

	for line in list_read:
		word 	= line[0]
		display = line[1]
		guess 	= line[2]
		time 	= line[3]
		means 	= set(line[4:])
		vocapy_set = VocapySet(word, int(display), int(guess), float(time))
		vocapy_set.update(means)
		dictionary[word] = vocapy_set

	return dictionary

def load_sessions(path):

	lst = list()
	list_read = load_csvfile(path)

	for line in list_read:
		new_line = [
			float(line[0]),
			int(line[1]),
			int(line[2]),
			int(line[3])
			]
		lst.extend([new_line])

	return lst

def load_csvfile(path):

	list_read = list()

	try:
		with open(path) as csv_file:
			reader = csv.reader(csv_file)
			for line in reader:
				list_read.append(line)
		return list_read
	except IOError as ioerr:
		return list()

def save_dict(dictionary, path):

	list_write = list()

	for word in dictionary.keys_sorted_list():
		l = [
			word, 
			dictionary[word].display, 
			dictionary[word].guess, 
			dictionary[word].time
		]
		l.extend(dictionary[word].means_sorted_list())
		list_write.append(l)

	save_csvfile(list_write, path)

def save_csvfile(list_write, path, mode='w'):

	try:
		with open(path, mode) as csv_file:
			writer = csv.writer(csv_file)
			writer.writerows(list_write)
	except IOError as ioerr:
		print(ioerr)

def main():
	pass

	
if __name__ == '__main__':
	main()
