import logging
from collections import defaultdict


class Rates:
	def __init__(self):
		self.exchange = defaultdict(dict)

	def set_conversion(self, src, dst, rate):
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

            self.category2spent = defaultdict(dict)
            self.category2transactions = defaultdict(list) # [category] -> (amount, currency, what)
            self.totalSpent = defaultdict(float)
            self.totalLimit = None

            self.aisp_api = None
            self.api_client = None
            self.auth_api = None
            self.bank = None
            self.auth_url = None
            self.begin_url = None

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
                print("processed_transactions", processed_transactions)
                for category, array in processed_transactions.items():
                        if category not in self.categories:
                                raise ValueError("Unknown category.")
                        for amount, currency, what in array:
                            for destination in self.currencies:
                                if destination not in self.category2spent[category]:
                                    self.category2spent[category][destination] = 0.0
                                self.category2spent[category][destination] += \
                                        amount * self.rates.exchange[currency][destination]
                                self.category2transactions[category].append(
                                        (amount, currency, what))
                                self.totalSpent[destination] += amount * self.rates.exchange[
                                        currency][destination]

class UserModel:
    def __init__(self, currencies, rates, categories):
        self.currencies = currencies
        self.rates = rates
        self.categories = categories
        self.models = {}

    def get(self, user):
        if user not in self.models:
            self.models[user] = Model(self.currencies, self.rates, self.categories)
        return self.models[user]



