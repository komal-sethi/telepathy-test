import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

class Game(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    sender_id = db.Column(db.String(100), nullable=False)
    receiver_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')

class User(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

@app.route('/auth/google', methods=['POST'])
def google_auth():
    token = request.json.get('token')
    try:
        # Verify Google ID token
        idinfo = id_token.verify_oauth2_token(token, requests.Request())
        
        # Extract user info
        user_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')

        # Check or create user
        user = User.query.get(user_id)
        if not user:
            user = User(id=user_id, email=email, name=name)
            db.session.add(user)
            db.session.commit()

        return jsonify({
            'user_id': user_id,
            'email': email,
            'name': name
        }), 200

    except ValueError:
        return jsonify({'error': 'Invalid token'}), 400

@socketio.on('create_game')
def create_game(data):
    sender_id = data['sender_id']
    game_id = f"game_{os.urandom(8).hex()}"
    
    game = Game(id=game_id, sender_id=sender_id)
    db.session.add(game)
    db.session.commit()
    
    emit('game_created', {'game_id': game_id}, room=sender_id)

@socketio.on('invite_player')
def invite_player(data):
    receiver_email = data['email']
    game_id = data['game_id']
    
    # In a real app, you'd send an email invitation here
    # For now, we'll just broadcast
    emit('game_invitation', {
        'game_id': game_id, 
        'sender_email': data['sender_email']
    }, room=receiver_email)

@socketio.on('join_game')
def on_join(data):
    game_id = data['game_id']
    user_id = data['user_id']
    
    join_room(game_id)
    
    # Update game with receiver
    game = Game.query.get(game_id)
    game.receiver_id = user_id
    game.status = 'active'
    db.session.commit()
    
    emit('game_joined', {'game_id': game_id}, room=game_id)

@socketio.on('card_selected')
def handle_card_selection(data):
    game_id = data['game_id']
    card_index = data['card_index']
    user_id = data['user_id']
    
    # Broadcast card selection to all in game room
    emit('card_selected_update', {
        'card_index': card_index,
        'user_id': user_id
    }, room=game_id)

@socketio.on('check_card')
def check_card(data):
    game_id = data['game_id']
    card_index = data['card_index']
    is_correct = data['is_correct']
    
    emit('card_check_result', {
        'card_index': card_index,
        'is_correct': is_correct
    }, room=game_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=5000)
