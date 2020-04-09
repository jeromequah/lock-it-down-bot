# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import datetime
import os 

# your code begins here 

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True

# Step 03: add database configurations here
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://projectuser:smt203proj@localhost:5432/projectdb" 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Student, Booking, Locker

# Step 05: add routes and their binded functions here
valid_Schools = ['SIS', 'SOA', 'SOE','LKCSB','SOL']
valid_Levels = ['2','3']
valid_Numbers = [str(i) for i in range(1,51)]
valid_Sizes = ['S', 'M', 'L'] 

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/postLocker/', methods=['POST'])
def postLocker():

	lockerSchool = request.json['lockerSchool']
	lockerLevel = request.json['lockerLevel']
	lockerNumber = request.json['lockerNumber']
	lockerSize = request.json['lockerSize']
	lockerAvailability = 'Yes'
	errors = {}

	try:
		if lockerSchool.upper() not in valid_Schools:   
			errors['School Error'] = '{} is an invalid school. Please enter a valid school.'.format(lockerSchool)
			
		if (lockerLevel.isdigit() == False) or (lockerLevel not in valid_Levels):        
			errors['Level Error'] = '{} is an invalid level. Please enter a valid level.'.format(lockerLevel)
		
		if (lockerNumber.isdigit() == False) or (lockerNumber not in valid_Numbers):
			errors['Number Error'] = '{} is an invalid locker number. Please enter a valid locker number between 1 to 50.'.format(lockerNumber)

		if lockerSize not in valid_Sizes:
			errors['Size Error'] = '{} is an invalid size. Please enter a valid size.'.format(lockerSize)

		if len(errors) >= 1:
			return jsonify(errors)
	
		else:
			lockerName = lockerSchool + '-' + 'L' + lockerLevel + '-' + lockerNumber		
			
			# check if locker already exists in database
			locker = Locker.query.filter_by(lockerName=lockerName).first()  
			if locker is None:
				new_locker = Locker(lockerName=lockerName, lockerSize=lockerSize, lockerSchool= lockerSchool, lockerLevel=lockerLevel, lockerNumber = lockerNumber, lockerAvailability = lockerAvailability)
				db.session.add(new_locker)
				db.session.commit()
				print("Your booking details have been posted successfully.")
				return jsonify(new_locker.serialize())
			else: 
				return jsonify('{} already exists in database. Please review locker details (i.e. school, level, number) and try again.'.format(lockerName))
	
	except Exception as e:
		return (str(e)) 

@app.route('/postBooking/', methods=['POST'])
def postBooking():
	matric = request.json['matric']
	lockerName = request.json['lockerName']
	errors = {}

	try:
		locker = Locker.query.filter_by(lockerName=lockerName).first()

		if (matric.isdigit() == False) or len(str(matric)) != 8:
			errors['Matric Error'] = '{} is an invalid matric ID. Please enter a valid matric ID.'.format(matric)
			
		if not(type(lockerName) == str) or locker is None:
			errors['Locker Error'] = '{} does not exist. Please try again.'.format(lockerName)

		if len(errors) >= 1:
			return jsonify(errors)

		else:
			student = Student.query.filter_by(matric=matric).first()
			if student is None:
				new_student = Student(matric=matric)
				db.session.add(new_student)
				db.session.commit() 
				new_booking = Booking(matric=matric, lockerName=lockerName)
				db.session.add(new_booking)
				db.session.commit()
				return jsonify(new_booking.serialize())
			else:
				new_booking = Booking(matric=matric, lockerName=lockerName)
				db.session.add(new_booking)
				db.session.commit()
				return jsonify(new_booking.serialize())

	except Exception as e:
		return (str(e))

@app.route('/getBooking/', methods= ['GET'])
def getBooking():
	errors = {}
	try:
		if 'bookingID' in request.args:
			if request.args.get('bookingID').isdigit() == False:
				errors['BookingID Error'] = '{} is an invalid Booking ID. Please enter a valid booking ID.'.format(request.args.get('bookingID'))
				return jsonify(errors)
			else:
				id = int(request.args.get('bookingID'))
				booking = Booking.query.filter_by(bookingID=id).first()
				if booking == None:
					errors['BookingID Error'] = 'Booking ID {} does not exist. Please try again.'.format(id)
					return jsonify(errors)
				else:
					return jsonify(booking.serialize())
		else:
			getBooking = Booking.query.all()
			return jsonify([b.serialize() for b in getBooking])
	except Exception as e:
		return (str(e))

@app.route('/getLocker/', methods=['GET'])
def getLocker():

	errors = {}

	try:
		if 'lockerSchool' in request.args and 'lockerSize' in request.args: 
			lockerSchool = str(request.args.get('lockerSchool'))
			lockerSize = str(request.args.get('lockerSize'))
			
			if lockerSchool.upper() not in valid_Schools:   
				errors['School Error'] = '{} is an invalid school. Please enter a valid school.'.format(lockerSchool)
			
			if lockerSize not in valid_Sizes:
				errors['Size Error'] = '{} is an invalid size. Please enter a valid size.'.format(lockerSize)

			if len(errors) >= 1:
				return jsonify(errors)
				
			else: 
				getLocker = Locker.query.filter(and_(Locker.lockerSchool == lockerSchool, Locker.lockerSize == lockerSize))
				return jsonify([g.serialize() for g in getLocker])

		elif 'lockerSchool' in request.args:
			lockerSchool = str(request.args.get('lockerSchool'))
			if lockerSchool.upper() not in valid_Schools:   
				errors['School Error'] = '{} is an invalid school. Please enter a valid school.'.format(lockerSchool)
				return jsonify(errors)
			
			else:
				getLocker = Locker.query.filter(Locker.lockerSchool == lockerSchool).all()
				return jsonify([g.serialize() for g in getLocker])

		elif 'lockerSize' in request.args:
			lockerSize = str(request.args.get('lockerSize'))
			if lockerSize not in valid_Sizes:
				errors['Size Error'] = '{} is an invalid size. Please enter a valid size.'.format(lockerSize)
				return jsonify(errors)
			else:
				getLocker = Locker.query.filter(Locker.lockerSize == lockerSize).all()
				return jsonify([g.serialize() for g in getLocker])
		else:
			getLocker = Locker.query.all()
			return jsonify([g.serialize() for g in getLocker])
		
	except Exception as e:
		return (str(e))

@app.route('/getLockerAvailability/', methods = ['GET'])
def getLockerAvailability():
	try:
		checker = []
		getLocker = Locker.query.all()
		print(getLocker)

		for locker in getLocker:
			print(locker.lockerAvailability)

			if locker.lockerAvailability == 'No':
				return str(1)

		return str(0)

	except Exception as e:
		return (str(e))
	 
@app.route('/updateBooking/<int:bookingID>', methods=['PUT'])
def updateBooking(bookingID):
	booking = Booking.query.get(bookingID)
	errors = {}
	
	try:
		if booking is None:
			errors['BookingID Error'] = 'Booking ID {} does not exist. Please try again.'.format(bookingID)
			return jsonify(errors)
		
		else:
			booking = Booking.query.filter_by(bookingID=bookingID).first()
			booking.timeout = datetime.datetime.now() 
			db.session.commit()
			print('Your booking details have been updated successfully.')
			return jsonify(booking.serialize())

	except Exception as e:
		return (str(e))

@app.route('/updateLocker/<lockerName>', methods=['PUT'])
def updateLocker(lockerName):
	errors = {}
	new_lockerAvailability = request.json['lockerAvailability']
	locker = Locker.query.get(lockerName)

	try:
		locker = Locker.query.filter_by(lockerName=lockerName).first()

		if not(type(lockerName) == str) or locker is None:
				errors['Locker Error'] = '{} does not exist. Please try again.'.format(lockerName)
				return jsonify(errors)

		elif (new_lockerAvailability != "Yes") and (new_lockerAvailability != "No"):
			errors['Availability Error'] = "Please key in a valid availability string 'Yes' or 'No'"
			return jsonify(errors)

		else:
			locker.lockerAvailability = new_lockerAvailability
			db.session.commit()
			print("Your locker details have been updated successfully.")
			return jsonify(locker.serialize())

	except Exception as e:
		return (str(e))

if __name__ == '__main__':
	app.run(debug=True)