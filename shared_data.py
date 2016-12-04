#!/usr/bin/env python

import ConfigParser
import feedparser
import pycurl, cStringIO
from math import ceil, sqrt
from multiprocessing import Manager, Process
import os, sys

DATA_POINTS = 40

if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
	feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')

# shared memory between processes
manager = Manager()
headlines = manager.list()
quotes = manager.list()

# configuration grab
cp = ConfigParser.SafeConfigParser()
cp.read(os.path.join(
	os.path.abspath(os.path.curdir),
	os.path.dirname(sys.argv[0]),
	'dashing.conf'
))

feeds = []
stocks_list = []

i = 0
while cp.has_option('headlines', 'feeds{}'.format(i)):
	val = cp.get('headlines', 'feeds{}'.format(i))
	if val.find('::') != -1:
		name, url = val.split('::')
	else:
		name = ''
		url = val

	feeds.append((name, url))
	i += 1

i = 0
while cp.has_option('stocks', 'tickers{}'.format(i)):
	val = cp.get('stocks', 'tickers{}'.format(i))
	if val.find('::') != -1:
		name, symbol = val.split('::')
	else:
		name = ''
		symbol = val

	stocks_list.append((name, symbol))
	i += 1

stocks = {}
for i in range(0, len(stocks_list)):
	stocks[stocks_list[i][1]] = stocks_list[i][0]

# grid count information
GRID_COUNT = len(stocks_list)
GRID_WIDTH = ceil(sqrt(len(stocks_list)))
GRID_HEIGHT = int(ceil(len(stocks_list)/GRID_WIDTH))
GRID_WIDTH = int(GRID_WIDTH)

# functions
def mesh_headlines(feeds):
	headlines = []

	for name, url in feeds:
		data = feedparser.parse(url)
		if name == '':
			name = data['feed']['title'].encode('ascii', errors='ignore')

		for entry in data['entries']:
			headlines.append({
				'title': entry['title'].encode('ascii', errors='ignore'),
				'published': entry['published_parsed'],
				'feed_title': name
			})

	headlines.sort(key=lambda x: x['published'])
	return headlines

def update_headlines():
	for i in range(0, len(headlines)):
		headlines.pop(0)

	for headline in mesh_headlines(feeds):
		headlines.append("{} ({})".format(
			headline['title'], headline['feed_title']
		))

	return headlines

def quotes_order(quote):
	for i in range(0, len(stocks_list)):
		if stocks_list[i][1] == quote['symbol']:
			return i

def update_quotes():
	url = "http://finance.yahoo.com/d/quotes.csv?s={}&f=sc1p2oghl1".format(
		"+".join(stocks.keys())
	)

	buf = cStringIO.StringIO()

	curl = pycurl.Curl()
	curl.setopt(pycurl.URL, url)
	curl.setopt(pycurl.WRITEFUNCTION, buf.write)
	curl.setopt(pycurl.FOLLOWLOCATION, 1)
	curl.perform()
	data = buf.getvalue()

	data = data.replace('"', "")
	quote_lines = data.split("\n")

	new_quotes = []

	for line in quote_lines:
		fields = line.split(",")

		if len(fields) == 7:
			new_quotes.append({
				'symbol': fields[0],
				'change': fields[1],
				'pctchange': fields[2],
				'open': fields[3],
				'low': fields[4],
				'high': fields[5],
				'last': fields[6]
			})

	new_quotes.sort(key=lambda x: quotes_order(x))

	if len(quotes) == DATA_POINTS:
		quotes.pop(DATA_POINTS-1)

	quotes.insert(0, new_quotes)

def update_headlines_threaded():
	proc = Process(target=update_headlines)
	proc.start()

def update_quotes_threaded():
	proc = Process(target=update_quotes)
	proc.start()
