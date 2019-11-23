import logging


class Rates:
	def __init__(self):
		self.exchange = {}
		
	def set_conversion(src, dst, rate):
		self.exchange[src][src] = 1
		self.exchange[dst][dst] = 1
		self.exchange[src][dst] = rate
		self.exchange[dst][src] = 1./rate

	def convert(src, dst, amount):
		return amount * self.exchange[src][dst]



class Model:
	def __init__(self, currencies, rates, categories):
		self.rates = rates 				# [src][dst] -> rate
		self.currencies = currencies	# list of currencies
		self.account2amount_converted = {}		# [account][currency] -> amount
		self.account2amount_splitted = {}		# [account][currency] -> amount
		self.currency2amount_converted = {}		# [currency] -> amount
		self.currency2amount_splitted = {}		# [currency] -> amount
		self.total = 0					# amount
		self.categories = categories	# list of categories
		self.category2amount = []		# [category][currency] -> amount
		self.category2limit = []		# [category][currency] -> limit
		self.total_limit = None

	def addProcessedTransactions(self, processed_transactions, account):
		for category, array in processed_transactions:
			if category not in self.categories:
				raise ValueError("Unknown category.")
			for amount, currency in array:
				self.account2amount_splitted +=

		raise NotImplemented


