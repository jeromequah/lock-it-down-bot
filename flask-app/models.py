import datetime
from app import db

class Student(db.Model):
	__tablename__ = 'student'
	matric= db.Column(db.String(8), primary_key=True)

#one to many
	student_booking = db.relationship('Booking', back_populates='student_info', uselist=True, cascade='all, delete-orphan', lazy=True)

	def __init__(self, matric, bookings=None):
		self.matric = matric
		self.bookings = []

	def __repr__(self):
		return '<matric {}>'.format(self.matric)

	def serialize(self):
		return {'matric': self.matric}

class Booking(db.Model):
	__tablename__ = 'booking'
	bookingID = db.Column(db.Integer, primary_key=True)
	matric = db.Column(db.String(8), db.ForeignKey('student.matric'), nullable=False)
	lockerName = db.Column(db.String(80), db.ForeignKey('locker.lockerName'), nullable=False)
	timein = db.Column(db.DateTime,default=datetime.datetime.now)
	timeout =  db.Column(db.DateTime)

#one to many
	student_info = db.relationship('Student', back_populates='student_booking')
	locker_info = db.relationship('Locker', back_populates='booking_info')
	
	def __init__(self, matric, lockerName):
		self.matric = matric
		self.lockerName = lockerName
		
	def __repr__(self):
		return '<booking id {}>'.format(self.bookingID)

	def serialize(self):
		return {
			'booking id': self.bookingID, 
			'matric': self.matric,  
			'lockerName': self.lockerName, 
			'time in': self.timein,
			'time out': [] if self.timeout == None else self.timeout #KIV-Ask Prof
			}

class Locker(db.Model):
	__tablename__ = 'locker'
	lockerName = db.Column(db.String(20), primary_key=True)
	lockerSchool = db.Column(db.String(20), unique=False, nullable=False)
	lockerLevel = db.Column(db.String(20), unique=False, nullable=False)
	lockerNumber = db.Column(db.String(2), unique=False, nullable=False)
	lockerSize = db.Column(db.String(20), unique=False, nullable=False)
	lockerAvailability = db.Column(db.String(20), unique=False, nullable=False)

 #one to many
	booking_info = db.relationship('Booking', back_populates='locker_info', uselist=True, cascade='all, delete-orphan', lazy=True)

	def __init__(self, lockerName, lockerSchool, lockerLevel, lockerNumber, lockerSize, lockerAvailability, booking_info=None):
		self.lockerName = lockerName
		self.lockerSchool = lockerSchool
		self.lockerLevel = lockerLevel
		self.lockerNumber = lockerNumber
		self.lockerSize = lockerSize
		self.lockerAvailability = lockerAvailability
		self.booking_info = []

	def __repr__(self):
		return '<locker name {}>'.format(self.lockerName)

	def serialize(self):
		return { 
				'locker name': self.lockerName, 
				'locker school': self.lockerSchool, 
				'locker level': self.lockerLevel,
				'locker number': self.lockerNumber,
				'locker size': self.lockerSize,
				'locker availability': self.lockerAvailability} 