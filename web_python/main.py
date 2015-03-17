#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colorsys
import json
import os
import random
import time
import sys

import tornado.ioloop
import tornado.web
import tornado.websocket

from fluent import sender
from fluent import event

clients = []
smartphones = []
hue = 0
emotions = ['アンニュイな気持ち', '興奮中', '眠い。。。', '気分爽快！', 'さっさと帰りたい気分']

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render(os.path.join('templates', 'index.html'))

	def post(self):
		global clients, hue, smartphones, emotions

		keys = ['like', 'interest', 'concentration', 'drowsiness', 'stress']
		data = {'time': int(time.time())}

		for key in keys:
			data[key] = int(self.get_argument(key))

		event.Event('kansei', data)

		print data
		sys.stdout.flush()
	
		for client in clients:
			print data
			client.write_message(json.dumps(data))

		resp = {'success': True}

		hue = (hue + random.randint(5, 10)) % 255
		sat = min(255, data['like'] + data['interest'] + data['concentration'])
		bri = max(0, 255 - (data['drowsiness'] + data['stress']) * 1.5)

		rgb = colorsys.hsv_to_rgb(hue / 255.0, sat / 255.0, bri / 255.0)
		resp['color'] = '#%02x%02x%02x' % (rgb[0] * 255, rgb[1] * 255, rgb[2] * 255)
		resp['emotion'] = random.choice(emotions)

		for smartphone in smartphones:
			smartphone.write_message(json.dumps(resp))

		return self.write(json.dumps(resp))

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		global clients

		if self not in clients:
			clients.append(self)

	def on_close(self):
		global clients

		if self in clients:
			clients.remove(self)

	def on_error(self):
		global clients

		if self in clients:
			clients.remove(self)

class SmartphoneHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		global smartphones

		if self not in smartphones:
			smartphones.append(self)

	def on_close(self):
		global smartphones

		if self in smartphones:
			smartphones.remove(self)

	def on_error(self):
		global smartphones

		if self in smartphones:
			smartphones.remove(self)

if __name__ == '__main__':
	sender.setup('td.eeg_datasets', host = 'localhost', port = 24224)

	application = tornado.web.Application([
		(r'/', MainHandler),
		(r'/ws', WebSocketHandler),
		(r'/sp', SmartphoneHandler),
	], static_path = os.path.join(os.path.dirname(__file__), 'static'))

	application.listen(80)
	tornado.ioloop.IOLoop.instance().start()
