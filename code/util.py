import logging
import enablebanking

from urllib.parse  import urlparse, parse_qs
from collections import defaultdict


class Categorizer():
    def __init__(self):
        self.categories = [
            'hotels',
            'transport',
            'food',
            'health',
            'cash',
            'other',
        ]

        self.keywords = {
            'hotels' : ['hotel', 'booking', 'airbnb'],
            'transport' : ['bus', 'flight', 'lot'],
            'food' : ['bar', 'restaurant', 'cafe', 'mcdonalds', 'starbucks', 'kfc', 'biedronka'],
            'health' : ['apotheka', 'apteka', 'medical'],
            'cash'   : ['bankomacie', 'bankomat'],
            'other'  : [None]
        }

    def get_categories(self):
        return self.categories

    def assign_category(self, description):
        for category in self.categories:
            keywords = self.keywords[category]
            for key in keywords:
                if key in description.lower() or key is None:
                    return category


def analyzeTransactions(raw_transactions: list):
    transaction_list = raw_transactions['transactions']
    categorizer = Categorizer()
    result = defaultdict(list)
    for item in transaction_list:
        amount = float(item['transaction_amount']['amount'])
        currency = item['transaction_amount']['currency']
        description = item['remittance_information'][0]
        category = categorizer.assign_category(description)
        result[category].append( (amount, currency, descripton) )
    return result, categorizer.categories


def createUserActionString(url, begin):
    text = "Please, open this page in browser: " + url + "\n"
    text += "Login, authenticate and copy paste back the URL where you got redirected." + "\n"
    text += "URL: (starts with %s): " % begin
    return text


def recomputeModel(account2api: dict):
	raise NotImplemented


def parse_redirected_url(redirected_url):
    """Parse query string into dict"""
    return {x: y[0] for x, y in parse_qs(urlparse(redirected_url).query).items()}

