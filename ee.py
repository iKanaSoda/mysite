import os
from bottle import Bottle, run, template, request, redirect, static_file, response
from win10toast import ToastNotifier
import pyautogui
import base64
import numpy as np
from datetime import datetime, timedelta

toaster = ToastNotifier()

# Dictionary mapping usernames to passwords
user_credentials = {
    'Princess': 'iloveyou',
    'admin': 'admin'
    }

is_admin = False

# Create a Bottle web application
app = Bottle()

# Shared variable to store the number
number = 5

# Dictionary mapping numbers to emojis and descriptions
emoji_data = {
    1: {'emoji': '😭', 'description': 'Very sad'},
    2: {'emoji': '😢', 'description': 'Sad'},
    3: {'emoji': '😤', 'description': 'Angry'},
    4: {'emoji': '😠', 'description': 'Very angry'},
    5: {'emoji': '😐', 'description': 'Neutral'},
    6: {'emoji': '🙂', 'description': 'Happy'},
    7: {'emoji': '😊', 'description': 'Very happy'},
    8: {'emoji': '🤘', 'description': 'Rock ____!'},
    9: {'emoji': '💦', 'description': 'Horny Asf'},
    10: {'emoji': '🍑💦', 'description': 'Feeling spicy'}
}

# Define the reference datetime
reference_datetime = datetime(2023, 5, 10, 14, 22)

# Define a route for the sign-in page
@app.route('/signin')
def signin():
    return '''
        <form action="/signin" method="post">
            <label>Username:</label><br>
            <input type="text" name="username"><br>
            <label>Password:</label><br>
            <input type="password" name="password"><br><br>
            <input type="submit" value="Sign In">
        </form>
    '''

# Define a route to handle sign-in form submission
@app.route('/signin', method='POST')
def do_signin():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if username in user_credentials and user_credentials[username] == password:
        # If credentials are correct, set a cookie and redirect to home page
        response.set_cookie('username', username)
        log_entry = f'{datetime.now()} - Username: {username}, IP: {request.environ.get("REMOTE_ADDR")}, Action: signed in.'
        save_log(log_entry)
        redirect('/')
    else:
        return 'Invalid username or password.'

# Define a route for the home page
@app.route('/')
def home():
    global username
    global is_admin
    username = request.get_cookie('username')
    if username:
        global number
        if number is None:
            return 'No number has been set.'
        else:
            emoji_info = emoji_data.get(number)
            if emoji_info:
                emoji = emoji_info['emoji']
                description = emoji_info['description']
            else:
                emoji = 'Unknown'
                description = 'Unknown'

            client_ip = request.environ.get('REMOTE_ADDR')
            print('Client IP:', client_ip)

            # Save log entry
            log_entry = f'{datetime.now()} - Username: {username}, IP: {client_ip}, Action: visited home page.'
            save_log(log_entry)

            # Calculate time differences
            current_datetime = datetime.now()
            time_difference = current_datetime - reference_datetime

            # Convert time difference to days, weeks, months, years, and decades
            days = int(time_difference.days)
            weeks = int(days // 7)
            months = int(current_datetime.month - reference_datetime.month + (current_datetime.year - reference_datetime.year) * 12)
            years = int(current_datetime.year - reference_datetime.year)
            decades = int(years // 10)

            # Convert time difference to hours and seconds
            total_hours = int(time_difference.total_seconds() / 3600)
            total_seconds = int(time_difference.total_seconds())

            if username == 'admin':
                is_admin = True
                print('ADMIN LOGGED IN')
                logs_button = '<form id="logsForm" method="get" action="/logs"><button type="submit" style="border-radius: 12px; background-color: #FFA07A; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px;">View Logs</button></form>'
            else:
                is_admin = False
                logs_button = ''

            return template(
                f'''<div style="background-color: pink; text-align: center; padding: 270px;">
                <h1>{emoji}</h1>
                <p>{description}</p>
                <form id="notificationForm">
                    <input type="text" name="message" placeholder="Enter your message">
                    <button type="submit" style="border-radius: 12px; background-color: #77DD77; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px;">Send Notification</button>
                </form>
                <form id="imageForm" enctype="multipart/form-data" method="post" action="/upload_image">
                    <input type="file" name="image" accept="image/*">
                    <button type="submit" style="border-radius: 12px; background-color: #FFD700; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px;">Upload Image</button>
                </form>
                {logs_button}
                <form id="screenshotForm" method="post" action="/take_screenshot">
                    <button type="submit" style="border-radius: 12px; background-color: #FFA07A; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px;">Take Screenshot</button>
                </form>
                <div>
                    <p>Days: {days}</p>
                    <p>Weeks: {weeks}</p>
                    <p>Months: {months}</p>
                    <p>Years: {years}</p>
                    <p>Decades: {decades}</p>
                    <p>Total Hours: {total_hours}</p>
                    <p>Total Seconds: {total_seconds}</p>
                </div>
                </div>
                <form id="logoutForm" method="post" action="/logout" style="position: absolute; top: 10px; right: 10px;">
                    <button type="submit" style="border-radius: 12px; background-color: #FFA07A; border: none; color: white; padding: 5px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 12px;">Logout</button>
                </form>
                <script>
                    document.getElementById('notificationForm').addEventListener('submit', function(event) {{
                        event.preventDefault();
                        var message = document.getElementById('notificationForm').elements['message'].value;
                        fetch('/send_notification', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: JSON.stringify({{message: message}})
                        }}).then(response => {{
                            if (response.ok) {{
                                alert('Notification sent successfully!');
                            }} else {{
                                alert('Failed to send notification.');
                            }}
                        }});
                    }});
                </script>
                , emoji=emoji, description=description, days=days, weeks=weeks, months=months, years=years, decades=decades, total_hours=total_hours, total_seconds=total_seconds)'''
            )
            
    else:
        redirect('/signin')


# Define a route to update the number
@app.route('/update_number', method='POST')
def update_number():
    global number
    data = request.json
    number = data.get('number')
    log_entry = f'{datetime.now()} - Username: admin, IP: {request.environ.get("REMOTE_ADDR")}, Action: changed number to {number}.'
    save_log(log_entry)
    return 'Number updated successfully.'

# Define a route to send a notification
@app.route('/send_notification', method='POST')
def send_notification():
    data = request.json
    message = data.get('message')
    # Add logic to send the notification here
    toaster.show_toast('Notification', message)
    log_entry = f'{datetime.now()} - Username: {request.get_cookie("username")}, IP: {request.environ.get("REMOTE_ADDR")}, Action: sent notification.'
    save_log(log_entry)
    return 'Notification sent.'

# Define a route to handle image upload
@app.route('/upload_image', method='POST')
def upload_image():
    if 'image' not in request.files:
        return 'No file uploaded'

    image = request.files['image']
    if image.filename == '':
        return 'No file selected'

    # Ensure that the "uploads" directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Save the uploaded image
    save_path = os.path.join('uploads', image.filename)
    image.save(save_path)

    log_entry = f'{datetime.now()} - Username: {request.get_cookie("username")}, IP: {request.environ.get("REMOTE_ADDR")}, Action: uploaded image.'
    save_log(log_entry)

    return f'Image uploaded successfully. Saved as {save_path}'

# Define a route to take a screenshot
@app.route('/take_screenshot', method='POST')
def take_screenshot():
    # Take a screenshot
    screenshot_path = os.path.join('uploads', 'screenshot.png')
    pyautogui.screenshot(screenshot_path)
    # Redirect to a new route that serves the screenshot
    redirect('/screenshot')
    log_entry = f'{datetime.now()} - Username: {request.get_cookie("username")}, IP: {request.environ.get("REMOTE_ADDR")}, Action: took screenshot.'
    save_log(log_entry)
    return

# Define a route to serve the screenshot
@app.route('/screenshot')
def serve_screenshot():
    if is_admin:
        log_entry = f'{datetime.now()} - Username: {request.get_cookie("username")}, IP: {request.environ.get("REMOTE_ADDR")}, Action: served screenshot.'
        save_log(log_entry)
        return static_file('screenshot.png', root='uploads', mimetype='image/png')
        toaster.show_toast('Notification', 'Screen Shot Taken: ADMIN')
    
    else:
        toaster.show_toast('Notification', 'Screen Shot Requested')
        a = input('y/n : ')
        if a == 'y':
            log_entry = f'{datetime.now()} - Username: {request.get_cookie("username")}, IP: {request.environ.get("REMOTE_ADDR")}, Action: served screenshot.'
            save_log(log_entry)
            return static_file('screenshot.png', root='uploads', mimetype='image/png')
        else:
            return None

# Define a route for logout
@app.route('/logout', method='POST')
def logout():
    response.delete_cookie('username')
    log_entry = f'{datetime.now()} - Username: {request.get_cookie("username")}, IP: {request.environ.get("REMOTE_ADDR")}, Action: logged out.'
    save_log(log_entry)
    redirect('/signin')

def save_log(log_entry):
    with open('access_logs.txt', 'a') as log_file:
        log_file.write(log_entry + '\n')

# Function to read logs from the file
def read_logs():
    logs = []
    if os.path.exists('access_logs.txt'):
        with open('access_logs.txt', 'r') as log_file:
            logs = log_file.readlines()
    return logs

# Function to clear logs
def clear_logs():
    if os.path.exists('access_logs.txt'):
        os.remove('access_logs.txt')

@app.route('/logs', method=['GET', 'POST'])
def view_logs():
    if request.method == 'POST':
        new_number = request.forms.get('number')
        if new_number.isdigit():
            global number
            number = int(new_number)
            return 'Number updated successfully.'
        else:
            return 'Invalid number.'
    else:
        logs = read_logs()
        logs_output = '<br>'.join(logs)
        change_number_form = '''
            <form method="post" action="/logs">
                <label for="number">Enter new emoji number:</label>
                <input type="text" id="number" name="number">
                <input type="submit" value="Change">
            </form>
        '''
        return logs_output + '<br><br>' + change_number_form

if __name__ == '__main__':
    # Run the Bottle app
    run(app, host='0.0.0.0', port=80)
