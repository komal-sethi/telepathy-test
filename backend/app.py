import os
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
from geventwebsocket.websocket import WebSocket

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logger.info('Database configured with Supabase PostgreSQL')

# Configure CORS - most permissive settings
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["*"],
        "allow_headers": "*",
        "expose_headers": "*",
        "max_age": 86400,
        "supports_credentials": False,
        "send_wildcard": True,
        "vary_header": False
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    logger.debug(f"Response headers: {dict(response.headers)}")
    return response

# Configure SocketIO with enhanced WebSocket support
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent',
    logger=True,
    engineio_logger=True,
    ping_timeout=60000,
    ping_interval=25000,
    transports=['polling', 'websocket'],
    always_connect=True,
    path='/socket.io',
    cookie=False,
    manage_session=False,
    allow_upgrades=True,
    max_http_buffer_size=1e8,
    handle_session=False,
    cors_credentials=False
)

logger.info(f"Starting application with DATABASE_URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

db = SQLAlchemy(app)

@app.route('/health')
def health_check():
    logger.info("Health check endpoint called")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request path: {request.path}")
    response = jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "request_info": {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers)
        }
    })
    return response

class Game(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    sender_id = db.Column(db.String(100), nullable=False)
    receiver_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')

class User(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

@app.route('/auth/google', methods=['POST', 'OPTIONS'])
def google_auth():
    if request.method == 'OPTIONS':
        return '', 204

    logger.info("Google auth endpoint called")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request data: {request.get_data(as_text=True)}")

    try:
        token = request.json.get('token')
        if not token:
            logger.error("No token provided in request")
            return jsonify({'error': 'No token provided'}), 400

        logger.debug(f"Verifying Google token")
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not client_id:
            logger.error("GOOGLE_CLIENT_ID environment variable not set")
            return jsonify({'error': 'Server configuration error'}), 500

        logger.debug(f"Using client_id: {client_id[:10]}...")
        
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            client_id
        )
        
        if not idinfo:
            logger.error("Token verification returned no info")
            return jsonify({'error': 'Token verification failed'}), 400

        logger.info(f"Token verified for user email: {idinfo.get('email')}")
        
        user_id = idinfo.get('sub')
        email = idinfo.get('email')
        name = idinfo.get('name', '')

        if not user_id or not email:
            logger.error(f"Missing required user info. user_id: {bool(user_id)}, email: {bool(email)}")
            return jsonify({'error': 'Invalid token data'}), 400

        try:
            # Check or create user
            user = User.query.get(user_id)
            if not user:
                logger.info(f"Creating new user with email: {email}")
                user = User(id=user_id, email=email, name=name)
                db.session.add(user)
                db.session.commit()
            else:
                logger.info(f"Existing user found with email: {email}")

            return jsonify({
                'user_id': user_id,
                'email': email,
                'name': name
            }), 200

        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            db.session.rollback()
            return jsonify({'error': 'Database error', 'details': str(db_error)}), 500

    except ValueError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return jsonify({'error': 'Invalid token', 'details': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in google_auth: {str(e)}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('create_game')
def create_game(data):
    logger.info(f"Creating game with data: {data}")
    try:
        sender_id = data['sender_id']
        game_id = f"game_{os.urandom(8).hex()}"
        
        game = Game(id=game_id, sender_id=sender_id)
        db.session.add(game)
        db.session.commit()
        
        logger.info(f"Game created successfully: {game_id}")
        emit('game_created', {'game_id': game_id}, room=sender_id)
    except Exception as e:
        logger.error(f"Error creating game: {str(e)}")
        emit('error', {'message': 'Failed to create game'})

@socketio.on('invite_player')
def invite_player(data):
    logger.info(f"Inviting player with data: {data}")
    try:
        receiver_email = data['email']
        game_id = data['game_id']
        
        emit('game_invitation', {
            'game_id': game_id, 
            'sender_email': data['sender_email']
        }, room=receiver_email)
        logger.info(f"Invitation sent to {receiver_email}")
    except Exception as e:
        logger.error(f"Error sending invitation: {str(e)}")
        emit('error', {'message': 'Failed to send invitation'})

@socketio.on('join_game')
def on_join(data):
    logger.info(f"Player joining game with data: {data}")
    try:
        game_id = data['game_id']
        user_id = data['user_id']
        
        join_room(game_id)
        
        game = Game.query.get(game_id)
        game.receiver_id = user_id
        game.status = 'active'
        db.session.commit()
        
        logger.info(f"Player {user_id} joined game {game_id}")
        emit('game_joined', {'game_id': game_id}, room=game_id)
    except Exception as e:
        logger.error(f"Error joining game: {str(e)}")
        emit('error', {'message': 'Failed to join game'})

@socketio.on_error()
def error_handler(e):
    logger.error(f"SocketIO error: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        logger.info("Creating database tables...")
        db.create_all()
        logger.info("Database tables created successfully")
    
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
