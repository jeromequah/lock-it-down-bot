# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# your code begins here 

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True

# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://projectuser:password@localhost:5432/projectdb" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Student, Booking, Locker

# Step 05: add routes and their binded functions here
@app.route('/postLocker/', methods=['POST'])
def create_locker():
    print('create_locker')
    locker_name = request.json['lockerName']
    locker_size = request.json['lockerSize']
    locker_school = request.json['lockerSchool']
    locker_level = request.json['lockerLevel']
    locker_availability = 'Yes'

    try:
        new_locker = Locker(lockerName=locker_name, lockerSize=locker_size, lockerSchool= locker_school, lockerLevel=locker_level, lockerAvailability = locker_availability)
        db.session.commit()
        return jsonify('{} was created'.format(new_locker))

    except Exception as e:
        return (str(e))

@app.route('/postBooking/', methods=['POST'])
def create_booking():
    print('create_booking')
    matric = request.json['matric']
    locker_name = request.json['lockerName']

    try:
        new_student = Student(matric=matric)
        db.session.add(new_student)
        db.session.commit() 
        new_booking = Booking(matric=matric, lockerName=locker_name)
        db.session.add(new_booking)
        db.session.commit()
        return jsonify('{} was created'.format(new_booking))

    except Exception as e:
        return (str(e))

# your code ends here 

if __name__ == '__main__':
	app.run(debug=True)