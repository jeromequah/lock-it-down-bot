import logging # to inform when and why things don't work as expected

from telegram import ReplyKeyboardMarkup 
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

my_token = '1021081111:AAEe7HbsD4tRE9RrndctArLggjH1Z-6IPiU'

# Flow of Conversation
MATRIC_VALIDITY, FILTER_LOCATION, FILTER_SIZE, AVAIL_LOCKER, BOOKING_CONFIRMED = range(5) 

# Store user info in temp dictionary for referencing 
user_info = {} 


# Start - Introduction to Lock-It-Down Bot & User inputs Matriculation Number 
def start(update, context): 

    context.bot.send_message(chat_id=update.effective_chat.id, 
                            text='Hello Student! \n \n'
                            'Heard you need a locker! Our locker rates are at $0.03/hour. '
                            'You can request a locker by your desired location and locker size. \n \n'
                            'Before we begin, please enter your SMU Matriculation Number: ')

    return MATRIC_VALIDITY


# Check for validity of Matriculation Number (8 characters)
def matric_validity(update, context):

    matric_id = update.message.text
    user_info['matric id'] = matric_id

    if len(str(matric_id)) == 8:
        reply_keyboard = [['YES']]
        update.message.reply_text("Alright! Select 'YES' to start your booking. \n \n"
                                  "Note: You may type /cancel at any time to terminate your session.", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return FILTER_LOCATION 

    # else:
    #     print('exception case needed') # (!) Need to code exception case      


# Select Filter Location 
def filter_location(update, context):

    reply_keyboard = [['LKCSB', 'SOA', 'SOE'], ['SOL', 'SIS']]
    update.message.reply_text('Select Locker Location:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FILTER_SIZE 


# Select Filter Locker Size 
def filter_size(update, context):

    location = update.message.text
    user_info['location'] = location

    reply_keyboard = [['S'], ['M'], ['L']]
    update.message.reply_text('Select Locker Size:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return AVAIL_LOCKER 


# Select From Available Lockers
## temporary dummy values, need GET request to pull available lockers from database, based on user's filter requests. ##
def avail_locker(update, context):

    size = update.message.text
    user_info['locker size'] = size

    reply_keyboard = [['SIS-L1-01'], ['SIS-L1-05'], ['SIS-L2-11'], ['SIS-L3-01'], ['SIS-L3-12'], ['SIS-L3-33']] 
    update.message.reply_text('Select Locker To Confirm Booking:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return BOOKING_CONFIRMED


def booking_confirmed(update, context): 

    selected = update.message.text
    user_info['selected locker'] = selected

    update.message.reply_text('Done! Please head to {}'.format(user_info['selected locker'])) 

    print(user_info)

    return ConversationHandler.END 


def cancel(update, context): 
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text("Your session has been terminated. Please type /start to begin a new one.")

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(my_token, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            MATRIC_VALIDITY: [MessageHandler(Filters.text, matric_validity)], # must receive text(matric id) first

            FILTER_LOCATION: [MessageHandler(Filters.regex('^(YES)$'), filter_location)], # must receive YES 

            FILTER_SIZE: [MessageHandler(Filters.regex('^(LKCSB|SOA|SOE|SOL|SIS)$'), filter_size)], # must receive locker location first

            AVAIL_LOCKER: [MessageHandler(Filters.regex('^(S|M|L)$'), avail_locker)], # must receive locker size first

            BOOKING_CONFIRMED: [MessageHandler(Filters.text, booking_confirmed)] # (!!!) Need to change filter to accept locker xxx-xx-xx only 

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)


    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
