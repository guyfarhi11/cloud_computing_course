from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_lot.db'
db = SQLAlchemy(app)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), nullable=False)
    parking_lot = db.Column(db.String(20), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

@app.route('/entry', methods=['POST'])
def entry():
    plate = request.args.get('plate')
    parking_lot = request.args.get('parkingLot')
    new_ticket = Ticket(plate=plate, parking_lot=parking_lot)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify({'ticket_id': new_ticket.id}), 201

@app.route('/exit', methods=['POST'])
def exit():
    ticket_id = request.args.get('ticketId')
    ticket = Ticket.query.get(ticket_id)
    if ticket and not ticket.exit_time:
        ticket.exit_time = datetime.utcnow()
        db.session.commit()
        parked_time = ticket.exit_time - ticket.entry_time
        parked_minutes = parked_time.total_seconds() / 60
        charge = math.ceil(parked_minutes / 15) * 2.5  # $10/hour => $2.5/15min
        return jsonify({
            'license_plate': ticket.plate,
            'total_parked_time': str(parked_time),
            'parking_lot_id': ticket.parking_lot,
            'charge': charge
        }), 200
    return jsonify({'error': 'Invalid ticket ID or already exited'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
