from flask import Flask, render_template, request, jsonify, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# File paths
USERS_FILE = "users.txt"
RESERVATIONS_FILE = "reservations.txt"


# Helper functions to read and write to text files
def read_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as file:
        users = file.readlines()
    return [user.strip().split(',') for user in users]


def write_users(users):
    with open(USERS_FILE, 'w') as file:
        for user in users:
            file.write(','.join(user) + '\n')


def read_reservations():
    if not os.path.exists(RESERVATIONS_FILE):
        return []
    with open(RESERVATIONS_FILE, 'r') as file:
        reservations = file.readlines()
    return [reservation.strip().split(',') for reservation in reservations]


def write_reservations(reservations):
    with open(RESERVATIONS_FILE, 'w') as file:
        for reservation in reservations:
            file.write(','.join(reservation) + '\n')


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    users = read_users()
    user = next((user for user in users if user[0] == username and user[1] == password), None)

    if user:
        session['username'] = username  # Store username in session
        return jsonify({'status': 'success', 'role': user[2]})
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect username or password'})


@app.route('/register', methods=['POST'])
def register():
    new_username = request.form['newUsername']
    new_password = request.form['newPassword']

    users = read_users()

    if any(user[0] == new_username for user in users):
        return jsonify({'status': 'error', 'message': 'Username already exists'})

    # Add new user to users.txt
    users.append([new_username, new_password, 'user'])
    write_users(users)

    return jsonify({'status': 'success', 'message': 'Registration successful'})


@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'You must be logged in to make a reservation'})

    dog_name = request.form['dogName']
    owner_name = request.form['ownerName']
    breed = request.form['breed']
    age = request.form['age']
    special_req = request.form['specialReq']
    date = request.form['date']
    username = session['username']  # Get the logged-in user's username

    reservations = read_reservations()
    confirmation_number = f"CN{len(reservations) + 1}"

    # Add username to the reservation details
    reservation = [confirmation_number, dog_name, owner_name, breed, age, special_req, date, username]
    reservations.append(reservation)
    write_reservations(reservations)

    return jsonify({'status': 'success', 'confirmationNumber': confirmation_number})


@app.route('/get_reservations', methods=['GET'])
def get_reservations():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'You must be logged in to view reservations'})

    username = session['username']
    reservations = read_reservations()

    # Filter reservations based on the logged-in user's username
    user_reservations = [reservation for reservation in reservations if reservation[7] == username]

    return jsonify({'status': 'success', 'reservations': user_reservations})


if __name__ == '__main__':
    app.run(debug=True)
