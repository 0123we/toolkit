from flask import Flask, request, jsonify, render_template, send_file
from datetime import timedelta, datetime
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
# import db and model
from models import db, User, History
import openai
import re
from flask_socketio import SocketIO, emit
from flask_migrate import Migrate


app = Flask(__name__)
# sqlite database file path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatrobot.db'
# The key used to generate and validate the token
app.config['JWT_SECRET_KEY'] = 'secretkey'
# The token is valid for 2 hours
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
# SHA-512 is a stronger version of SHA-256 with a longer hash length, thereby providing HMAC-SHA512 with
# higher collision resistance and security.
connected_users = {}
# Create a JWT manager instance
jwt = JWTManager(app)
# Initialize db
db.init_app(app)
migrate = Migrate(app, db)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
migrate = Migrate(app, db)
# first step to migrate:flask db init
# second step to migrate:flask db migrate
# thirdly step to migrate:flask db upgrade


# Route for the homepage, returns the home.html page
@app.route('/', methods=["GET"])
def index():
    return render_template('home.html')


# Route for the signup page, returns the signup.html page
@app.route('/signup-page', methods=["GET"])
def signup_page():
    return render_template('signup.html')


# Flask route decorator to specify the URL pattern for the route and HTTP methods allowed
@app.route('/users', methods=['POST'])
def create_user():
    # Get the form data from the request JSON payload
    form_data = request.get_json()
    first_name = form_data.get('first_name')
    last_name = form_data.get('last_name')
    phone = form_data.get('phone')
    email = form_data.get('email')
    password = form_data.get('password')
    # Regex pattern for validating the email address
    email_regex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    # Check if the email address matches the regex pattern
    if not re.match(email_regex, email):
        # If not, return an error response with an invalid email format message
        return jsonify(code=-1, msg='Invalid email format.', token=''), 400
    # Check if the password is less than 6 characters long
    if len(password) < 6:
        # If so, return an error response with a short password message
        return jsonify(code=-2, msg='Password must be at least 6 characters long.', token=''), 400
    # Check if there is already a user with the same email address
    if User.query.filter_by(email=email).first():
        # If so, return an error response with a user exists message
        return jsonify(code=-3, msg='User exists.', token=''), 409
    # Create a new User object with the form data
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        # Hash the password with SHA-256
        password=generate_password_hash(password, method='sha256')
    )
    # Add the new user to the database session
    db.session.add(new_user)
    # Commit the session to write the changes to the database
    db.session.commit()
    # Create a JWT token for the new user
    Token = create_access_token(identity=new_user.id)
    # Return a success response with the JWT token
    return jsonify(code=0, token=Token, msg='success'), 201


# Login page route, returns the login.html page
@app.route('/login-page', methods=['GET'])
def login_page():
    return render_template('login.html')


# User login route, validates username and password, if correct, returns a JWT token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(code=-1, msg='User does not exist.'), 404

    if not check_password_hash(user.password, password):
        return jsonify(code=-2, msg="Password Error."), 401

    Token = create_access_token(identity=user.id)
    return jsonify(code=0, token=Token), 200


# This decorator handles the connect event when a client connects to the SocketIO server
@socketio.on('connect')
def handle_connect():
    # Get the JWT token from the request arguments
    token = request.args.get('token')
    # Decode the JWT token to get the user ID
    user_id = decode_token(token)
    # Add the user ID to the connected_users dictionary, using the session ID as the key
    connected_users[request.sid] = user_id['sub']


# This decorator handles the disconnect event when a client disconnects from the SocketIO server
@socketio.on('disconnect')
def handle_disconnect():
    # If the session ID exists in the connected_users dictionary, remove it
    if request.sid in connected_users:
        user_id = connected_users[request.sid]
        del connected_users[request.sid]


# Search page route, returns the search.html page
@app.route('/search_page', methods=["GET"])
def search_page():
    return render_template('search.html')


# Voice page route, returns the voice.html page
@app.route('/messages/voice', methods=["GET"])
def voice():
    return render_template('voice.html')


# Get user information route, returns the initial of the user's last name
@app.route("/user_id", methods=["GET"])
# Protect the route. To access this route, users must provide a valid JWT in the request.
@jwt_required()
def user_id_info():
    user_id = get_jwt_identity()
    get_user_lastname = User.query.get(user_id)

    if get_user_lastname:
        return jsonify(
            last_name_initial=get_user_lastname.last_name[0].upper()
        )

    return jsonify(message="User not found"), 404


# Check login status route, if the user is logged in, returns confirmation message
@app.route('/check_login', methods=['GET'])
# Protect the route. To access this route, users must provide a valid JWT in the request.
@jwt_required()
def check_login():
    return jsonify(message="User is logged in"), 200


# History page route, returns the history.html page
@app.route('/history', methods=["GET"])
def history():
    return render_template('history.html')


@app.route('/Neuralink', methods=["GET"])
def Neuralink():
    return render_template('Neuralink.html')


# Product page route, returns the product.html page
@app.route('/product', methods=["GET"])
def product():
    return render_template('product.html')


# Documentation page route, returns the documentation.html page
@app.route('/documentation', methods=["GET"])
def documentation():
    return render_template('documentation.html')


# Introduction page route, returns the intro.html page
@app.route('/intro', methods=["GET"])
def intro():
    return render_template('intro.html')


# Guide page route, returns the guide.html page
@app.route('/guide', methods=["GET"])
def guide():
    return render_template('guide.html')


# Contact us page route, returns the contactus.html page
@app.route('/contactus', methods=["GET"])
def contactus():
    return render_template('contactus.html')


if __name__ == '__main__':
    with app.app_context():
        app.run(host='0.0.0.0')
        db.create_all()
        socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
