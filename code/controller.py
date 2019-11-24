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
            /help -- prints this help message
            /add BANK  -- adds accounts from a user in the specified bank
                possible options: [Alior, KIR].
            /show total CUR -- prints sum of values in all accounts converted to currency CUR
            /show balances [CUR] -- prints all account balances in the currency CUR, or in default currency if not specified
            /show transactions [CATEGORY] -- shows all transactions per category (if specified), or just all transactions
            /summary CATEGORY -- gives summary for the category
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


def summary(update, context):
    raise NotImplemented


def show(update, context):
    raise NotImplemented


def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text("Conversation Cancelled.")
    return ConversationHandler.END


class Controller():
	def __init__(self):
            self.token='1032122116:AAFMa6ewEqjbV9cYsu34kekzLJZo7ITq3Jw'
            self.model = None
            self.add_callback = BankAdderCallback(self.model)

	def run(self):
            updater = Updater(self.token, use_context=True)
            dispatcher = updater.dispatcher
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help))

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

