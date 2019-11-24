import logging


class Rates:
	def __init__(self):
		self.exchange = {}

	def set_conversion(src, dst, rate):
		self.exchange[src][src] = 1
		self.exchange[dst][dst] = 1
		self.exchange[src][dst] = rate
		self.exchange[dst][src] = 1./rate


class Model:
	def __init__(self, currencies, rates, categories):
		self.rates = rates 				# [src][dst] -> rate
		self.currencies = currencies	# list of currencies
		self.categories = categories	# list of categories

		self.account2info = {}		# [account] -> (amount, currency)
		self.totalBalance = defaultdict(float)	# [currency] -> amount

		self.category2spent = defaultdict(dict)       # [category][currency] -> amount
                self.category2transactions = defaultdict(list) # [category] -> (amount, currency, what)
                self.totalSpent = defaultDict(float)
		self.totalLimit = None

        def setLimit(self, limit, currency):
            self.totalLimit = defaultdict(float)
            for destination in self.currencies:
                self.totalLimit[destination] = limit * self.rates.exchange[currency][destination]

        def addAccount(self, account, balance, currency):
            self.account2info[account] = (balance, currency)
            for destination in self.currencies:
                self.totalBalance[destination] += balance * self.rates.exchange[
                        currency][destination]

	def addProcessedTransactions(self, processed_transactions, account):
		for category, array in processed_transactions:
			if category not in self.categories:
				raise ValueError("Unknown category.")
			for amount, currency, what in array:
                            for destination in self.currencies:
                                self.category2spent[category][destination] += \
                                        amount * self.rates.exchange[currency][destination]
                                self.category2transactions[category].append(
                                        (amount, currency, what))
                                self.totalSpent[destination] += amount * self.rates.exchange[
                                        currency][destination]

