from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math

app = Flask(__name__)

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_lot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), nullable=False)
    parking_lot = db.Column(db.String(20), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime)


# Create the database within the application context
with app.app_context():
    db.drop_all()  # Drop all old db tables
    db.create_all()

@app.route('/entry', methods=['POST'])
def entry():
    """
    Handle vehicle entry into the parking lot.
    Expects 'plate' and 'parkingLot' parameters.
    Returns the ticket ID.
    """
    plate = request.args.get('plate')
    parking_lot = request.args.get('parkingLot')
    
    if not plate or not parking_lot:
        # Case for missing parking lot or plate
        return jsonify({'error': 'plate or parking lot does not exists'}), 200

    existing_ticket = Ticket.query.filter_by(plate=plate, exit_time=None).first()
    
    if existing_ticket:
        if parking_lot!=existing_ticket.parking_lot:
            # Return the existing ticket ID if the vehicle is already parked
            return jsonify({'error': f"Plate is already signed in parking lot {existing_ticket.parking_lot}"}), 200
        else:
            # Return the existing ticket ID if the vehicle is already parked
            return jsonify({'ticket_id': existing_ticket.id}), 200
    
     
    new_ticket = Ticket(plate=plate, parking_lot=parking_lot)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify({'ticket_id': new_ticket.id}), 201

@app.route('/exit', methods=['POST'])
def exit():
    """
    Handle vehicle exit from the parking lot.
    Expects 'ticketId' parameter.
    Returns the license plate, total parked time, parking lot ID, and the charge.
    """
    ticket_id = request.args.get('ticketId')
    
    if not ticket_id:
        return jsonify({'error': 'Unmatched ticket id'
        }), 200
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket or ticket.exit_time:
        return jsonify({'error':'the ticket is not valid to exit'}), 200

    # Update ticket with exit time
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


if __name__ == '__main__':
    """
    Run the Flask application.
    """
    app.run(host='0.0.0.0', port=80)
