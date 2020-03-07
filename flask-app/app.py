from flask import Flask, request, jsonify 

app = Flask(__name__)

booking_info = [{'matric id': '01375548', 'location': 'SIS', 'locker size': 'S', 'selected locker': 'SIS-L1-01'},
{'matric id': '01374447', 'location': 'SIS', 'locker size': 'M', 'selected locker': 'SIS-L2-03'}]

locker_info = [{'locker name': 'SIS-L1-01', 'location': 'SIS', 'locker size': 'S', 'availability': 'Yes'}]

@app.route('/search/', methods=['GET']) 


def get_available_lockers():
    location = request.args.get('location')
    size = request.args.get('locker size')

    for locker in locker_info:
        if locker['location'] == location and locker['locker size'] == size and locker['availability'] == 'Yes':
            return locker['locker name']
            
if __name__ == '__main__':
    app.run(debug=True) # makes the flask app run in an infinite loop, 