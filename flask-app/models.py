import datetime
from app import db

class Student(db.Model):
    __tablename__ = 'student'
    matric= db.Column(db.String, primary_key=True)

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
    timein = db.Column(db.DateTime,default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    # timeout = db.Column(db.DateTime,default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    matric = db.Column(db.String, db.ForeignKey('student.matric'), nullable=False)
    lockerName = db.Column(db.String(80), db.ForeignKey('locker.lockerName'), nullable=False)

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
            'locker name': self.lockerName, 
            'time in': self.timein, 
            'time out': self.timeout}

class Locker(db.Model):
    __tablename__ = 'locker'
    lockerName = db.Column(db.String(20), primary_key=True)
    lockerSize = db.Column(db.String(20), unique=False, nullable=False)
    lockerSchool = db.Column(db.String(20), unique=False, nullable=False)
    lockerLevel = db.Column(db.String(20), unique=False, nullable=False)
    lockerAvailability = db.Column(db.String(20), unique=False, nullable=False)

 #one to many
    booking_info = db.relationship('Booking', back_populates='locker_info', uselist=True, cascade='all, delete-orphan', lazy=True)

    def __init__(self, lockerName, lockerSize, lockerSchool, lockerAvailability, lockerLevel, bookings=None):
        self.lockerName = lockerName
        self.lockerSize = lockerSize
        self.lockerSchool = lockerSchool
        self.lockerLevel = lockerLevel
        self.lockerAvailability = lockerAvailability
        self.bookings = []

    def __repr__(self):
        return '<locker name {}>'.format(self.lockerName)

    def serialize(self):
        return {'locker name': self.lockerName, 
                'locker school': self.lockerSchool, 
                'locker level': self.lockerLevel,
                'locker size': self.lockerSize, 
                'locker availability': self.lockerAvailability} 