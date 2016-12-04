#!/usr/bin/env python

#
# Dashing - tk_dashing.py
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: GPLv2
#

from Tkinter import Tk, END, Canvas, Frame, Text
from ttk import Label, LabelFrame
from tkFont import Font

from PIL import Image
from PIL.ImageTk import PhotoImage

from copy import deepcopy
from math import ceil, floor
from multiprocessing import Manager, Process
from os import unlink
from os.path import exists

import shared_data
from tk_window import tk_window

class tk_dashing(tk_window):
	_manager = None
	_txt_headtick = None
	_txt_stocktick = None
	_cvs_stocks = None
	_canvas = []
	_images = []
	_headlines = ""
	_headtick_pixels = 0
	_headtick_pixelold = 0
	_stocktick_pixels = 0
	_stocktick_pixelold = 0

	def __init__(self):
		super(tk_dashing, self).__init__('dashing', 'Dashing')
		self.setup()

	def setup(self):
		self.tk_setup()

	def tk_setup(self):
		self.set_title("Dashing")

		self.master.config({'bg': '#000000'})

		i = 0
		while i < shared_data.GRID_HEIGHT:
			self.master.rowconfigure(i, weight=5000)
			i += 1

		self.master.rowconfigure(i+1, weight=1)
		self.master.rowconfigure(i+2, weight=1)

		i = 0
		while i < shared_data.GRID_WIDTH:
			self.master.columnconfigure(i, weight=1)
			i += 1

		self._txt_headtick = Text(self.master)
		self._txt_headtick.config({
			'height': 1, 'bg': '#000000', 'fg': '#FFFFFF', 'wrap': 'none',
			'font': Font(size=20), 'padx': 10, 'pady': 0,
			'highlightcolor': '#000000', 'highlightthickness': 0,
			'insertbackground': '#000000', 'insertborderwidth': 0,
			'selectbackground': '#000000', 'selectborderwidth': 0,
			'borderwidth': 0, 'relief': 'flat'
		})

		self._txt_stocktick = Text(self.master)
		self._txt_stocktick.config({
			'height': 1, 'bg': '#000000', 'fg': '#FFFFFF', 'wrap': 'none',
			'font': Font(size=20), 'padx': 10, 'pady': 0,
			'highlightcolor': '#000000', 'highlightthickness': 0,
			'insertbackground': '#000000', 'insertborderwidth': 0,
			'selectbackground': '#000000', 'selectborderwidth': 0,
			'borderwidth': 0, 'relief': 'flat'
		})
		self._txt_stocktick.tag_config('pos', foreground='#00D000')
		self._txt_stocktick.tag_config('zero', foreground='#FFFFFF')
		self._txt_stocktick.tag_config('neg', foreground='#D00000')

		self._txt_stocktick.grid(
			row=shared_data.GRID_HEIGHT, column=0, rowspan=1,
			columnspan=shared_data.GRID_WIDTH, sticky='ew',
			padx=0, pady=0
		)
		self._txt_headtick.grid(
			row=shared_data.GRID_HEIGHT+1, column=0, rowspan=1,
			columnspan=shared_data.GRID_WIDTH, sticky='ew',
			padx=0, pady=0
		)

		for i in range(0, len(shared_data.stocks_list)):
			widget = self.create_canvas()
			widget.grid(
				row=int(floor(i/shared_data.GRID_WIDTH)),
				column=i%shared_data.GRID_WIDTH,
				sticky='nesw', padx=0, pady=0, ipadx=0, ipady=0
			)

		self.master.after(1000, self.update_stocks)
		self.master.after(1000, self.update_headlines)
		self.master.after(2000, self.scroll_stocks)
		self.master.after(2000, self.scroll_headlines)
		self.master.after(2000, self.update_plots)

	def finish_dataplots_thread(self):
		f = open('/tmp/dashing-done', 'w')
		f.write('1')
		f.close()

	def generate_dataplots(self, canvas_width, canvas_height):
		if (
			len(shared_data.quotes) == 0 or
			len(shared_data.quotes[0]) != shared_data.GRID_COUNT
		):
			self.finish_dataplots_thread()
			return

		#print(len(shared_data.quotes))
		#print(len(shared_data.quotes[0]))
		#print(shared_data.quotes)

		data = []
		for i in range(0, shared_data.GRID_COUNT):
			data.append(({},[],[]))

		for i in range(0, len(shared_data.quotes)):
			#quote_group = deepcopy(shared_data.quotes[i])
			quote_group = shared_data.quotes[i]

			for j in range(0, len(quote_group)):
				if (
					quote_group[j]['last'] != "N/A" and
					quote_group[j]['open'] != "N/A" and
					quote_group[j]['low'] != "N/A" and
					quote_group[j]['high'] != "N/A"
				):
					price_high = price_low = price_open = float(
						quote_group[j]['open']
					)

					data[j][1].append(i)
					data[j][2].insert(0, float(quote_group[j]['last']))

					if float(quote_group[j]['low']) < price_low:
						price_low = float(quote_group[j]['low'])
					elif float(quote_group[j]['high']) > price_high:
						price_high = float(quote_group[j]['high'])

				data[j][0]['symbol'] = quote_group[j]['symbol']
				data[j][0]['low'] = price_low
				data[j][0]['open'] = price_open
				data[j][0]['high'] = price_high

		# import inside the thread
		import matplotlib
		matplotlib.use('Agg')
		import matplotlib.pyplot as plt
		dpi=50.0
		for i in range(0, shared_data.GRID_COUNT):
			price_low = data[i][0]['low']
			price_open = data[i][0]['open']
			price_high = data[i][0]['high']
			price_offset = (price_high-price_low)*0.05

			fig = plt.figure(
				figsize=(
					int(ceil(canvas_width/dpi)),
					int(ceil(canvas_height/dpi))
				), dpi=int(dpi)
			)
			ax = fig.add_subplot(1,1,1, axisbg='#000000')

			# axes styling
			ax.spines['top'].set_color('#FFFFFF')
			ax.spines['top'].set_linewidth(3)
			ax.spines['left'].set_color('#FFFFFF')
			ax.spines['left'].set_linewidth(3)
			ax.spines['right'].set_color('#FFFFFF')
			ax.spines['right'].set_linewidth(3)
			ax.spines['bottom'].set_color('#FFFFFF')
			ax.spines['bottom'].set_linewidth(3)
			ax.xaxis.label.set_color('#FFFFFF')
			ax.yaxis.label.set_color('#FFFFFF')
			ax.tick_params(axis='x', colors='#000000') # supposed to be hidden
			ax.tick_params(axis='y', colors='#FFFFFF')
			ax.grid(True)

			ax.plot(data[i][1], data[i][2], color='#FFFFFF', linewidth=2)
			ax.set_ylim((price_low-price_offset, price_high+price_offset))
			ax.set_ylabel('{} ({})'.format(
				shared_data.stocks[data[i][0]['symbol']], data[i][2][0]
			), fontsize=25)
			ax.tick_params('y',
				direction='in', labelleft=False, labelright=True
			)

			ax.axhline(y=price_low, color='#FF0000', linewidth=2)
			ax.axhline(y=price_high, color='#00FF00', linewidth=2)
			if price_low != price_open and price_high != price_open:
				ax.axhline(y=price_open, color='#0000FF', linewidth=2)

			fig.savefig(
				"/tmp/dashing-{}.png".format(i), dpi=int(dpi),
				facecolor='#000000', edgecolor='#000000'
			)
			plt.close()

			img = Image.open("/tmp/dashing-{}.png".format(i))
			img = img.resize((canvas_width, canvas_height), Image.BILINEAR)
			img.save("/tmp/dashing-{}-final.png".format(i), format="png")

		self.finish_dataplots_thread()

	def update_plots(self, started=False):
		if not started:
			for i in range(0, shared_data.GRID_COUNT):
				if exists("/tmp/dashing-{}.png".format(i)):
					unlink("/tmp/dashing-{}.png".format(i))
				if exists("/tmp/dashing-{}-final.png".format(i)):
					unlink("/tmp/dashing-{}-final.png".format(i))

			proc = Process(target=self.generate_dataplots, args=(
				self._canvas[0].winfo_width(), self._canvas[0].winfo_height()
			))
			proc.start()
			started = True

		all_done = False
		if started:
			if exists('/tmp/dashing-done'):
				unlink('/tmp/dashing-done')
				all_done = True

			#for i in range(0, shared_data.GRID_COUNT):
				#if not exists("/tmp/dashing-{}-final.png".format(i)):
					#all_done = False
					#break

		if all_done:
			self._images = []
			for i in range(0, shared_data.GRID_COUNT):
				if exists("/tmp/dashing-{}-final.png".format(i)):
					img = PhotoImage(file="/tmp/dashing-{}-final.png".format(i))
					canvas_width = self._canvas[i].winfo_width()
					canvas_height = self._canvas[i].winfo_height()

					self._canvas[i].create_image(
						canvas_width/2, canvas_height/2, image=img
					)
					self._images.append(img)

			started = False

		self.master.after(1000, self.update_plots, started)

	def scroll_ticker(self, widget, ticker_text, pixel_old):
		widget_txt = widget.get(1.0, END)[0:-1]
		widget.xview_scroll(1, "pixel")

		ret = None

		if widget.xview()[1] == 1:
			if widget_txt.count(" -- ") == 1:
				ret = 'store'
				widget.insert(END, ticker_text)

			elif widget_txt.count(" -- ") == 2:
				ret = 'reset'
				widget.delete(1.0, '1.{}'.format(widget_txt.find(" -- ")+4))
				widget.xview_moveto(0.0)
				widget.insert(END, ticker_text)
				widget.xview_scroll(pixel_old, "pixel")

			else:
				ret = 'start'
				widget.insert(END, ticker_text)

		return ret

	def scroll_headlines(self):
		self._headtick_pixels += 1
		ret = self.scroll_ticker(
			self._txt_headtick, self._headlines, self._headtick_pixelold
		)
		if ret == 'store':
			self._headtick_pixelold = self._headtick_pixels
		elif ret == 'reset':
			self._headtick_pixels = self._headtick_pixelold

		self.master.after(10, self.scroll_headlines)

	def scroll_stocks(self):
		self._stocktick_pixels += 1
		ret = self.scroll_ticker(
			self._txt_stocktick, self._quotes, self._stocktick_pixelold
		)
		if ret == 'store':
			self._stocktick_pixelold = self._stocktick_pixels
		elif ret == 'reset':
			self._stocktick_pixels = self._stocktick_pixelold

		if ret is not None:
			self.tag_stocks()

		self.master.after(5, self.scroll_stocks)

	def update_headlines(self):
		shared_data.update_headlines_threaded()

		if len(shared_data.headlines) > 0:
			self._headlines = "{} -- ".format(" - ".join(shared_data.headlines))
			self.master.after(120000, self.update_headlines)
		else:
			self.master.after(1000, self.update_headlines)

	def tag_stocks(self):
		txt = self._txt_stocktick.get(1.0, END)[0:-1]

		start = 0
		while txt.find(" - ", start) != -1:
			end = txt.find(" - ", start)
			totalend = txt.find(" -- ", start)
			if totalend != -1 and (end == -1 or totalend < end):
				end = totalend

			if txt[start:end].find("+") != -1:
				self._txt_stocktick.tag_add('pos',
					"1.{}".format(start), "1.{}".format(end)
				)

			elif txt[start:end].find("-") != -1:
				self._txt_stocktick.tag_add('neg',
					"1.{}".format(start), "1.{}".format(end)
				)

			else:
				self._txt_stocktick.tag_add('zero',
					"1.{}".format(start), "1.{}".format(end)
				)

			start = end + 3

	def update_stocks(self):
		shared_data.update_quotes_threaded()
		self._quotes = ""

		if len(shared_data.quotes) > 0:
			for quote in shared_data.quotes[0]:
				self._quotes += "{} {} ({} {}) - ".format(
					shared_data.stocks[quote['symbol']],
					quote['last'], quote['change'], quote['pctchange']
				)

			self._quotes = self._quotes[0:len(self._quotes)-1] + "- "

		self.master.after(5000, self.update_stocks)

	def create_canvas(self, **kwargs):
		canvas = Canvas(self.master,
			background="#000000", highlightbackground="#000000"
		)
		self._canvas.append(canvas)
		return canvas
