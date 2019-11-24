import telegram

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from wrapper import APIWrapper
import util


# States for add dialogue.
CMD, LINK = range(2)


def start(update, context):
    update.message.reply_text("""Hi! I am Richard -- a bot for managing your finance.
            It can be Home Budget, or Private Budget, or any other thing you would like.
            For usage instructions, please use /help command.""")


def help(update, context):
    help_text = """
        Available commands:
            /start -- starts this bot
            /help -- prints this help message
            /add BANK  -- adds accounts from a user in the specified bank
                possible options: [Alior, KIR].

            /money CUR -- gives total balance in currency CUR
            /accounts  -- lists accounts and their balances

            /categories -- lists all available categories
            /spent CAT CUR -- amount spent to category CAT in currency CUR
            /transactions CAT -- lists transactions in category CAT

            /setlimit AMOUNT CUR -- sets limit to the amount AMOUNT in currency CUR
            /getlimit CUR -- prints the limit in currency CUR
            /freedom CUR  -- prints the freedom in currency CUR
            /paid    CUR  -- prints amount paid in currency CUR
    """
    update.message.reply_text(help_text)


class BankAdderCallback:
    def __init__(self, model):
        self.bank = None
        self.state = CMD
        self.wrapper = APIWrapper()
        self.model = model

    def __call__(self, update, context):
        if self.state is CMD:
            self.link, self.token, self.aisp_api = None, None, None
            self.state = LINK
            return self.initial_command_call(update, context)
        elif self.state is LINK:
            self.state = CMD
            return self.link_command_call(update, context)
        else:
            raise ValueError("Unknown State.")

    def initial_command_call(self, update, context):
        self.bank = str(update.message.text).strip().split()[1]
        message_text = str('Bank {} selected.'.format(self.bank))
        update.message.reply_text(message_text)
        wrapper = self.wrapper
        self.auth_url, self.begin_url,  (self.api_client, self.auth_api) = wrapper.getLoginURLandAPI(self.bank)
        update.message.reply_text(util.createUserActionString(self.auth_url, self.begin_url))
        assert self.state is LINK
        return self.state

    def link_command_call(self, update, context):
        self.link = update.message.text
        self.aisp_api, self.token = self.wrapper.getUserTokenAndAPI(self.bank, self.api_client, self.auth_api, self.link)
        self.add_info_to_model
        return ConversationHandler.END

    def add_info_to_model(self):
        # TODO(nekrald): UPDATE the model
        pass


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text("Conversation Cancelled.")
    return ConversationHandler.END

# Accounts
class DisplayAccountsCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented


class TotalBalanceCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented

# Transactions
class ListCategoriesCallback:
    def __init__(self, model):
            self.model = model
    def __call__(self, update, context):
        raise NotImplemented

class ShowCategoryTotalCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented

class ShowCategoryTransactionsCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented

# Limits
class SetLimitCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented

class ShowLimitCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented

class ShowFreedomCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented

class ShowSpentCallback:
    def __init__(self, model):
        self.model = model
    def __call__(self, update, context):
        raise NotImplemented




class Controller():
        def make_rates(self):
            self.rates = Rates()
            self.currencies = ['USD', 'EUR', 'GBP', 'PLN']
            self.rates.set_conversion('USD', 'PLN', 3.9)
            self.rates.set_conversion('EUR', 'PLN', 4.3)
            self.rates.set_conversion('GBP', 'PLN', 5.0)
            self.rates.set_conversion('EUR', 'USD', 1.1)
            self.rates.set_conversion('GBP', 'EUR', 1.16)
            self.rates.set_conversion('GBP', 'USD', 1.28)

	def __init__(self):
            self.make_rates()
            self.token='1032122116:AAFMa6ewEqjbV9cYsu34kekzLJZo7ITq3Jw'
            self.model = Model(currencies, rates, util.Categorizer().get_categories())

            self.add_callback = BankAdderCallback(self.model)

            self.balance_callback = TotalBalanceCallback(self.model)
            self.account_callback = DisplayAccountsCallback(self.model)

            self.list_category_callback = ListCategoriesCallback(self.model)
            self.category_spent_callback = ShowCategoryTotalCallback(self.model)
            self.category_transactions = ShowCategoryTransactionsCallback(self.model)

            self.set_limit_callback = SetLimitCallback(self.model)
            self.show_limit_callback = ShowLimitCallback(self.model)
            self.show_freedom_callback = ShowLimitCallback(self.model)
            self.paid_callback = ShowSpentCallback(self.model)

	def run(self):
            updater = Updater(self.token, use_context=True)
            dispatcher = updater.dispatcher

            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help))

            dispatcher.add_handler(CommandHandler("money", self.balance_callback))
            dispatcher.add_handler(CommandHandler("accounts", self.account_callback))

            dispatcher.add_handler(CommandHandler("categories", self.list_category_callback))
            dispatcher.add_handler(CommandHandler("spent", self.category_spent_callback))
            dispatcher.add_handler(CommandHandler("transactions", self.category_transactions)

            dispatcher.add_handler(CommandHandler("setlimit", self.set_limit_callback))
            dispatcher.add_handler(CommandHandler("getlimit", self.show_limit_callback))
            dispatcher.add_handler(CommandHandler("freedom", self.show_freedom_callback))
            dispatcher.add_handler(CommandHandler("paid", self.paid_callback))

            conv_handler = ConversationHandler(
                entry_points=[CommandHandler('add', self.add_callback)],
                states={
                    LINK : [MessageHandler(Filters.text, self.add_callback)]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )

            dispatcher.add_handler(conv_handler)

            updater.start_polling()
            updater.idle()

