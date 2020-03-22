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
        db.session.add(new_locker)
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

@app.route('/getBooking/', methods= ['GET'])
def get_booking():
    print('get_booking')
    
    #get Query Params of bookingID from URL
    if 'bookingID' in request.args:
        try:
            bookingID = int(request.args.get('bookingID'))
        except:
            return ('Please key in integers.')#error handle for non-digits
        booking = Booking.query.filter_by(bookingID = bookingID).first_or_404(description = 'BookingID {} not found. Please key in a valid bookingID.'.format(bookingID))
        #if booking not found, return 404 followed by comment 
        return jsonify(booking.serialize())
    else:
        booking = Booking.query.all()
        return jsonify([b.serialize() for b in booking])

@app.route('/getLocker/', methods=['GET'])
def get_locker():
    print('get_locker')

    '''Update 22/3/2020: 
    ---------------------
    * If Query Both School & Size, Only School will be taken
    '''

    #get Query Params of lockerSchool from URL
    if 'lockerSchool' in request.args: #if lockerSchool present in URL
        lockerSchool = str(request.args.get('lockerSchool'))
    
        if lockerSchool not in ('SIS','SOL','SOE','SOB','SOA'):
            return 'error_code: 404\n booking_error: {} is an invalid school.Please enter a valid school.'.format(lockerSchool)
        
        getLocker = Locker.query.filter_by(lockerSchool = lockerSchool).all()
        return jsonify([g.serialize() for g in getLocker])
        
   #if no lockerSchool Query, get using lockerSize Query
    elif 'lockerSize' in request.args: #if lockerSize present in URL
        lockerSize = str(request.args.get('lockerSize'))

        if lockerSize not in ('S','M','L'):
            return 'error_code: 404\n booking_error: {} is an invalid size.Please enter a valid lockersize.'.format(lockerSize)

        getLocker = Locker.query.filter_by(lockerSize = lockerSize).all()
        return jsonify([g.serialize() for g in getLocker])

    else: #if no params provided in URL
        getLocker = Locker.query.all()
        return jsonify([g.serialize() for g in getLocker])


@app.route('/updateBooking/<int:bookingID>', methods=['PUT'])
def update_booking(bookingID):
    booking = Booking.query.get(bookingID)
    booking.timeout = datetime.datetime.now()
    db.session.commit()
    return jsonify(booking.serialize())

@app.route('/updateLocker/<lockerName>', methods=['PUT'])
def update_locker(lockerName):
    new_lockerAvailability = request.json['lockerAvailability']
    locker = Locker.query.get(lockerName)
    locker.lockerAvailability = new_lockerAvailability
    db.session.commit()
    return jsonify(locker.serialize())
    
# your code ends here 

if __name__ == '__main__':
    app.run(debug=True)