import logging # to inform when and why things don't work as expected

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

my_token = 'insert token here'

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Hello Student! \n \nHeard you need a locker! Our locker rates are at $0.03/hour (+ more details), please select /getlocker to start your booking!")

def get_locker(update, context):
    keyboard = [[InlineKeyboardButton("Location", callback_data='Location'),
                 InlineKeyboardButton("Locker Type", callback_data='LockerType')],

                [InlineKeyboardButton("Cancel", callback_data='Cancel')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Filter your locker request by...', reply_markup=reply_markup)

def filter_location(update, context):
    keyboard = [[InlineKeyboardButton("LKCSB", callback_data='LKCSB'),
                 InlineKeyboardButton("SOA", callback_data='SOA'),
                 InlineKeyboardButton("SOE/SOSS", callback_data='SOE/SOSS'),
                 InlineKeyboardButton("SOL", callback_data='SOL'),
                 InlineKeyboardButton("SIS", callback_data='SIS')],

                [InlineKeyboardButton("Cancel", callback_data='Cancel')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Select Locker Location:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query # user's response
    query.edit_message_text(text="Selected Option: {}".format(query.data))

    if query.data == 'Location':
        filter_location(update, context)  


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(my_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('getlocker', get_locker))
    updater.dispatcher.add_handler(CommandHandler('filterlocation', filter_location))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()