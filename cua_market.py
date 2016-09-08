import numpy as np

class market:
	def __init__(self, pair, api):
		self.ORDERBOOK = ''
		self.OPENORDERS = ''
		self.HISTORY = ''
		self.PAIR = pair
		self.API = api
		
	def refreshOrderBook(self):
		self.ORDERBOOK = self.API.refreshOrderBook(self.PAIR)

	def refreshOpenOrders(self):
		self.OPENORDERS = self.API.refreshOpenOrders(self.PAIR)

	def refreshTradeHistory(self):
		self.HISTORY = self.API.refreshTradeHistory(self.PAIR)