import logging # to inform when and why things don't work as expected

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

import string, re, requests, json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

my_token = ''

# Flow of Conversation
MATRIC_VALIDITY, FILTER_LOCATION, FILTER_SIZE, AVAIL_LOCKER, BOOKING_START, DOUBLE_CHECK, BOOKING_END = range(7) 

user_info = {} # Store user info in temp dictionary for referencing 

base_url = 'https://lockitdownapp.herokuapp.com/'


# Start - Introduction to Lock-It-Down Bot & User inputs Matriculation Number 
def start(update, context): 

	context.bot.send_message(chat_id=update.effective_chat.id, 
							text='Please enter your SMU Matriculation Number:')

	return MATRIC_VALIDITY


def integer_validity(text):
	regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 
	if text.isdigit():
		return True


# Check for validity of Matriculation Number (8 characters)
def matric_validity(update, context):

	matric = update.message.text

	if len(str(matric)) == 8 and integer_validity(matric) == True: #matric id must be an integer of length 8 and must start with '01xxxxxx'
		user_info['matric'] = matric
		reply_keyboard = [['YES']]
		update.message.reply_text("Alright! Select 'YES' to start your booking. \n \n"
								  "Note: You may type /cancel at any time to terminate your session.", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
		return FILTER_LOCATION 

	elif matric == '/cancel': # Not sure whether need this here but I just put first 
		return cancel(update, context)

	else:
		update.message.reply_text('You have not entered a valid input! \nPlease try again!')     


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

def avail_locker(update, context):

	size = update.message.text
	user_info['locker size'] = size

	# Send API request to Flask App (getLocker) to pull available lockers from database, based on user's filtered request.
	params = {'lockerSchool': user_info['location'], 'lockerSize': user_info['locker size']}

	getLocker_url = base_url + 'getLocker/'
	r = requests.get(getLocker_url, params=params)


	# Sort API response into reply_keyboard
	reply_keyboard = [] 

	for locker in r.json():
		reply_keyboard.append([locker['locker name']])

	update.message.reply_text('Select Locker To Confirm Booking:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return BOOKING_START


def booking_start(update, context): 

	if update.message.text == '/cancel': # Not sure whether need this here but I just put first 
		return cancel(update, context)
	else:
		user_info['selected locker'] = update.message.text


	# Send API request to Flask App (postBooking) to post booking details to database.
	params = {'matric': user_info['matric'], 'lockerName': user_info['selected locker']}
	postBooking_url = base_url + 'postBooking/' 
	
	r = requests.post(postBooking_url, json=params)

	# Get booking id and store as global variable
	user_info['booking id'] = r.json()['booking id']
	print(user_info)

	# Send API request to Flask App (updateLocker) to update locker availability to No.
	params = {'lockerAvailability': 'No'}
	updateLocker_url = base_url + 'updateLocker/' + user_info['selected locker']
	
	r = requests.put(updateLocker_url, json=params)

	reply_keyboard = [['I want my things out!']] 
	update.message.reply_text("Done! Please head to your locker at: {} (School-Level-Number). \n \nPlease select the 'I want my things out!' option if you'd like to retrieve your items and end your session.".format(user_info['selected locker']), reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)) 

	return DOUBLE_CHECK


def double_check(update, context): 

	reply_keyboard = [['Yes please!']] 

	update.message.reply_text('Do you really want to retrieve your items now?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return BOOKING_END


def booking_end(update, context): 

	# Send API request to Flask App (updateBooking) to update booking
	updateBooking_url = base_url + 'updateBooking/' + str(user_info['booking id']) 

	r = requests.put(updateBooking_url) 

	

	# Send API request to Flask App (updateLocker) to update locker availability to Yes.
	params = {'lockerAvailability': 'Yes'}
	updateLocker_url = base_url + 'updateLocker/' + user_info['selected locker']

	r = requests.put(updateLocker_url, json=params)

	update.message.reply_text('Thank you for using Lock-It-Down! \n \n'
							'Enter /start again to begin a new booking session whenever you need a locker :D.')

	return ConversationHandler.END 


def cancel(update, context): 
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text("Your session has been terminated. Please type /start to begin a new one.", reply_markup=ReplyKeyboardRemove())

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

			BOOKING_START: [MessageHandler(Filters.text, booking_start)], # (!!!) might need to change filter to accept locker xxx-xx-xx only 

			DOUBLE_CHECK: [MessageHandler(Filters.regex('^(I want my things out!)$'), double_check)], # must receive 'I want my things out!'

			BOOKING_END: [MessageHandler(Filters.regex('^(Yes please!)$'), booking_end)], # must receive 'Yes please!'

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