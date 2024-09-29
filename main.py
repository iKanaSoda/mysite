from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, send, join_room
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # Ensure to set a secret key for sessions
socketio = SocketIO(app)

connected_users = {}

# Route for the homepage (login page)
@app.route('/')
def index():
    return render_template('login.html')

# Route to handle nickname and password submission
@app.route('/login', methods=['POST'])
def login():
    nickname = request.form['nickname']
    password = request.form['password']

    # Check if password is correct
    if password == "1234":  # Modify this for your actual password logic
        session['nickname'] = nickname  # Store the nickname in the session
        return render_template('chat.html', nickname=nickname)  # Render the chat page with nickname
    else:
        return "Incorrect password!", 401  # Return 401 Unauthorized if the password is wrong

# Handle incoming messages
@socketio.on('message')
def handle_message(data):
    nickname = data['nickname']
    message = data['message']
    print(f"{nickname}: {message}")
    send(f"{nickname}: {message}", broadcast=True)

# Handle new user joining
@socketio.on('join')
def on_join(data):
    nickname = data['nickname']
    join_room(nickname)
    connected_users[nickname] = request.sid
    send(f"{nickname} has joined the chat!", broadcast=True)

# Function to get the local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        ip = "127.0.0.1"
        print(f"Error getting IP address: {e}")
    return ip

if __name__ == '__main__':
    try:
        ip_address = get_local_ip()
        port = 80
        print(f"Server running! Access it at: http://{ip_address}:{port}/")
        socketio.run(app, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Failed to start the server: {e}")
