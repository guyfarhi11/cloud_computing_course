from flask import Flask, request, jsonify
import sqlite3
import uuid
import os
app = Flask(__name__)
DATABASE = 'messaging.db'

def connect_db():
    return sqlite3.connect(DATABASE)

def init_db():
    with connect_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY, 
                        name TEXT
                      )''')
        db.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY, 
                        sender_id TEXT, 
                        receiver_id TEXT, 
                        content TEXT
                      )''')
        db.execute('''CREATE TABLE IF NOT EXISTS blocks (
                        blocker_id TEXT, 
                        blocked_id TEXT
                      )''')
        db.execute('''CREATE TABLE IF NOT EXISTS groups (
                        id TEXT PRIMARY KEY, 
                        name TEXT
                      )''')
        db.execute('''CREATE TABLE IF NOT EXISTS group_members (
                        group_id TEXT, 
                        user_id TEXT
                      )''')
        db.execute('''CREATE TABLE IF NOT EXISTS group_messages (
                        group_id TEXT, 
                        sender_id TEXT, 
                        content TEXT
                      )''')
        db.commit()

# Initialize the database if it doesn't already exist
if not os.path.exists(DATABASE):
    init_db()

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    user_name = data['name']
    with connect_db() as db:
        cur = db.execute('SELECT * FROM users WHERE name = ?', (user_name,))
        if cur.fetchone():
            return jsonify({'error': f'User {user_name} is already registered.'}), 409
        user_id = str(uuid.uuid4())
        db.execute('INSERT INTO users (id, name) VALUES (?, ?)', (user_id, user_name))
        db.commit()
    return jsonify({'user_id': user_id, 'message': f'User {user_name} registered successfully'})

@app.route('/message', methods=['POST'])
def send_message():
    data = request.json
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    content = data['content']
    with connect_db() as db:
        cur = db.execute('SELECT * FROM users WHERE id = ?', (sender_id,))
        if not cur.fetchone():
            return jsonify({'error': 'Message not sent: Sender does not exist in the database.'}), 404
        cur = db.execute('SELECT * FROM users WHERE id = ?', (receiver_id,))
        if not cur.fetchone():
            return jsonify({'error': 'Message not sent: Receiver does not exist in the database.'}), 404
        cur = db.execute('SELECT * FROM blocks WHERE blocker_id = ? AND blocked_id = ?', (receiver_id, sender_id))
        if cur.fetchone():
            return jsonify({'error': 'You are blocked by the recipient.'}), 403
        message_id = str(uuid.uuid4())
        db.execute('INSERT INTO messages (id, sender_id, receiver_id, content) VALUES (?, ?, ?, ?)',
                   (message_id, sender_id, receiver_id, content))
        db.commit()
    return jsonify({'message_id': message_id})

@app.route('/block', methods=['POST'])
def block_user():
    data = request.json
    blocker_id = data['blocker_id']
    blocked_id = data['blocked_id']
    with connect_db() as db:
        # Verify both users exist
        cur = db.execute('SELECT * FROM users WHERE id = ?', (blocker_id,))
        if not cur.fetchone():
            return jsonify({'error': 'Blocker does not exist.'}), 404
        cur = db.execute('SELECT * FROM users WHERE id = ?', (blocked_id,))
        if not cur.fetchone():
            return jsonify({'error': 'Blocked user does not exist.'}), 404
        db.execute('INSERT INTO blocks (blocker_id, blocked_id) VALUES (?, ?)', (blocker_id, blocked_id))
        db.commit()
    return jsonify({'status': 'User blocked successfully'})

@app.route('/group', methods=['POST'])
def create_group():
    data = request.json
    group_name = data['name']
    with connect_db() as db:
        cur = db.execute('SELECT * FROM groups WHERE name = ?', (group_name,))
        existing_group = cur.fetchone()
        if existing_group:
            return jsonify({'message': f'Group "{group_name}" already exists'}), 400
        group_id = str(uuid.uuid4())
        db.execute('INSERT INTO groups (id, name) VALUES (?, ?)', (group_id, group_name))
        db.commit()
    return jsonify({'group_id': group_id, 'message': f'Group "{group_name}" created successfully'})

@app.route('/group/members', methods=['POST'])
def manage_group_members():
    data = request.json
    group_id = data['group_id']
    user_id = data['user_id']
    action = data['action']  # 'add' or 'remove'
    with connect_db() as db:
        cur = db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        if not cur.fetchone():
            return jsonify({'error': 'User does not exist'}), 404
        if action == 'add':
            cur = db.execute('SELECT * FROM group_members WHERE group_id = ? AND user_id = ?', (group_id, user_id))
            if cur.fetchone():
                return jsonify({'message': 'User already a member of the group'}), 400
            db.execute('INSERT INTO group_members (group_id, user_id) VALUES (?, ?)', (group_id, user_id))
            db.commit()
            return jsonify({'status': 'success', 'message': 'User added to the group'})
        elif action == 'remove':
            cur = db.execute('SELECT * FROM group_members WHERE group_id = ? AND user_id = ?', (group_id, user_id))
            if not cur.fetchone():
                return jsonify({'error': 'User is not a member of the group'}), 400
            db.execute('DELETE FROM group_members WHERE group_id = ? AND user_id = ?', (group_id, user_id))
            db.commit()
            return jsonify({'status': 'success', 'message': 'User removed from the group'})
    return jsonify({'status': 'success'})

@app.route('/group/message', methods=['POST'])
def send_group_message():
    data = request.json
    group_id = data['group_id']
    sender_id = data['sender_id']
    content = data['content']
    with connect_db() as db:
        cur = db.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
        existing_group = cur.fetchone()
        if not existing_group:
            return jsonify({'error': f'Group with id "{group_id}" does not exist'}), 404
        db.execute('INSERT INTO group_messages (group_id, sender_id, content) VALUES (?, ?, ?)', (group_id, sender_id, content))
        db.commit()
    return jsonify({'status': 'success', 'message': f'Message sent to group with id "{group_id}"'})

@app.route('/group/messages/<user_id>', methods=['GET'])
def check_group_messages(user_id):
    with connect_db() as db:
        cur = db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        if not cur.fetchone():
            return jsonify({'error': 'User does not exist'}), 404
        cur = db.execute('SELECT group_id FROM group_members WHERE user_id = ?', (user_id,))
        groups = [row[0] for row in cur.fetchall()]
        group_messages = []
        for group_id in groups:
            cur = db.execute('SELECT * FROM group_messages WHERE group_id = ?', (group_id,))
            messages = cur.fetchall()
            group_messages.extend(messages)
    return jsonify({'group_messages': group_messages})

@app.route('/messages/<user_id>', methods=['GET'])
def check_messages(user_id):
    with connect_db() as db:
        cur = db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        if not cur.fetchone():
            return jsonify({'error': 'User does not exist'}), 404
        cur = db.execute('SELECT * FROM messages WHERE receiver_id = ?', (user_id,))
        messages = cur.fetchall()
    return jsonify({'messages': messages})

if __name__ == '__main__':
    app.run(port=80)
