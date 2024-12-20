from flask import Flask, Response, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_mail import Mail, Message
import os, time, re, random, string
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'ARyan=!12'
 
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'aryan'
app.config['MYSQL_PASSWORD'] = 'ARyan=!12'
app.config['MYSQL_DB'] = 'clinic'
 
 
mysql = MySQL(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your SMTP server
app.config['MAIL_PORT'] = 587  # Use the appropriate port (587 for TLS)
app.config['MAIL_USERNAME'] = 'kanhayeoda@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'tnonqwviztvqqzey'  # Your email password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'kanhayeoda@gmail.com'

mail = Mail(app)


# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')  # Change this to your upload folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit the size of uploads to 16 MB

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def send_email(recipient, subject, body):
    msg = Message(subject=subject, recipients=[recipient], body=body)
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if len(username) == 2:  # Admin ID is 2 digits
                cursor.execute('''
                    SELECT a.admin_id, a.admin_name, al.password 
                    FROM Admin_Login al
                    JOIN Admin a ON al.admin_id = a.admin_id
                    WHERE al.admin_id = %s
                ''', (username,))
                account = cursor.fetchone()
                if account and check_password_hash(account['password'], password):
                    session['loggedin'] = True
                    session['id'] = account['admin_id']
                    session['role'] = 'admin'
                    session['user_name'] = account['admin_name']
                    return redirect(url_for('admin_page'))
                else:
                    flash('Incorrect username/password!', 'error')

            elif len(username) == 3:  # Receptionist ID is 3 digits
                cursor.execute('''
                    SELECT r.receptionist_id, r.receptionist_name, rl.password 
                    FROM Receptionist_Login rl
                    JOIN Receptionist r ON rl.receptionist_id = r.receptionist_id
                    WHERE rl.receptionist_id = %s
                ''', (username,))
                account = cursor.fetchone()
                if account and check_password_hash(account['password'], password):
                    session['loggedin'] = True
                    session['id'] = account['receptionist_id']
                    session['role'] = 'receptionist'
                    session['user_name'] = account['receptionist_name']
                    return redirect(url_for('receptionist_page'))
                else:
                    flash('Incorrect username/password!', 'error')

            elif len(username) == 4:  # Physiotherapist ID is 4 digits
                cursor.execute('''
                    SELECT p.physiotherapist_id, p.physiotherapist_name, pl.password 
                    FROM Physiotherapist_Login pl
                    JOIN Physiotherapist p ON pl.physiotherapist_id = p.physiotherapist_id
                    WHERE pl.physiotherapist_id = %s
                ''', (username,))
                account = cursor.fetchone()
                if account and check_password_hash(account['password'], password):
                    session['loggedin'] = True
                    session['id'] = account['physiotherapist_id']
                    session['role'] = 'physiotherapist'
                    session['user_name'] = account['physiotherapist_name']
                    return redirect(url_for('physiotherapist_page'))
                else:
                    flash('Incorrect username/password!', 'error')

            else:
                flash('Incorrect username/password!', 'error')
        except MySQLdb.Error as e:
            flash(f'Error: {str(e)}', 'error')
        except Exception as e:
            flash(f'An unexpected error occurred: {str(e)}', 'error')
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if email exists in any user table
        cursor.execute('SELECT * FROM Receptionist WHERE email = %s', (email,))
        user = cursor.fetchone()
        if not user:
            cursor.execute('SELECT * FROM Physiotherapist WHERE email = %s', (email,))
            user = cursor.fetchone()
        if not user:
            cursor.execute('SELECT * FROM Admin WHERE email = %s', (email,))
            user = cursor.fetchone()
        
        if user:
            user_id = user['receptionist_id'] if 'receptionist_id' in user else \
                    user['physiotherapist_id'] if 'physiotherapist_id' in user else \
                    user['admin_id']
            
            user_type = 'receptionist' if 'receptionist_id' in user else \
                        'physiotherapist' if 'physiotherapist_id' in user else \
                        'admin'
            otp = ''.join(random.choices(string.digits, k=6))
            cursor.execute('INSERT INTO PasswordResetRequests (user_type, user_id, otp) VALUES (%s, %s, %s)', (user_type, user_id, otp))
            mysql.connection.commit()
            
            # Send OTP via email
            subject = 'Your OTP Code for Password Reset'
            body = f'Your OTP code is {otp}. Use this code to reset your password.'
            send_email(email, subject, body)
            
            session['reset_user_id'] = user_id
            session['reset_user_type'] = user_type
            
            flash('OTP sent to your email!')
            return redirect(url_for('verify_otp'))
    
    else:
        flash('Email not found!', 'error')
    return render_template('forgot_password.html')


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM PasswordResetRequests WHERE otp = %s', (otp,))
        reset_request = cursor.fetchone()
        
        if reset_request:
            session['otp_verified'] = True
            user_id = session['reset_user_id']
            user_type = session['reset_user_type']
            return redirect(url_for('reset_password', user_id=user_id, user_type=user_type))
        else:
            flash('Invalid OTP!', 'error')

    return render_template('verify_otp.html')



@app.route('/reset_password/<user_id>/<user_type>', methods=['GET', 'POST'])
def reset_password(user_id, user_type):
    if 'otp_verified' not in session:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('loginpage'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        reverify_password = request.form['reverify_password']
        if new_password == reverify_password:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            hashed_password = generate_password_hash(new_password)

            # Update password based on user type
            if user_type == 'receptionist':
                cursor.execute('UPDATE Receptionist_Login SET password = %s WHERE receptionist_id = %s', (hashed_password, user_id))
            elif user_type == 'physiotherapist':
                cursor.execute('UPDATE Physiotherapist_Login SET password = %s WHERE physiotherapist_id = %s', (hashed_password, user_id))
            elif user_type == 'admin':
                cursor.execute('UPDATE Admin_Login SET password = %s WHERE admin_id = %s', (hashed_password, user_id))
            
            mysql.connection.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('loginpage'))
        else:
            flash('New passwords do not match!', 'error')
    return render_template('reset_password.html', user_id=user_id, user_type=user_type)



@app.route('/profile')
def profile():
    if 'loggedin' in session:
        user_id = session['id']
        role = session['role']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # Fetch user details based on role
            user = None
            name = None
            user_type = None
            
            if role == 'receptionist':
                cursor.execute('SELECT * FROM Receptionist WHERE receptionist_id = %s', (user_id,))
                user = cursor.fetchone()
                user_type = 'receptionist'
                name = user['receptionist_name'] if user else None

            elif role == 'physiotherapist':
                cursor.execute('SELECT * FROM Physiotherapist WHERE physiotherapist_id = %s', (user_id,))
                user = cursor.fetchone()
                user_type = 'physiotherapist'
                name = user['physiotherapist_name'] if user else None

            elif role == 'admin':
                cursor.execute('SELECT * FROM Admin WHERE admin_id = %s', (user_id,))
                user = cursor.fetchone()
                user_type = 'admin'
                name = user['admin_name'] if user else None

            # Ensure a default image is set if 'profile_image' is missing or empty
            # Ensure a default image is set if 'profile_image' is missing, empty, or None
            if user is not None:
                user['profile_image'] = user.get('profile_image') or 'default.jpg'

            # Pass user information to the profile template
            if user:
                return render_template('profile.html', user=user, id=user_id, name=name, user_type=user_type)
            else:
                flash('User not found.', 'error')
                return redirect(url_for('loginpage'))
        
        except MySQLdb.Error as e:
            flash(f'Error fetching user details: {str(e)}', 'error')
            return redirect(url_for('loginpage'))
    
    flash('You need to log in to perform this action.', 'warning')    
    return redirect(url_for('loginpage'))

@app.route('/update_details/<int:user_id>', methods=['GET', 'POST'])
def update_details(user_id):
    if 'loggedin' in session:
        role = session['role']  # Get the role from the session
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            # Handle the form submission for updating user details
            contact_number = request.form['contact_number']
            address = request.form['address']
            email = request.form['email']
            file = request.files.get('file')

            try:
                # Update user details based on role
                if role == 'receptionist':
                    cursor.execute('UPDATE Receptionist SET contact_number=%s, address=%s, email=%s WHERE receptionist_id=%s',
                                   (contact_number, address, email, user_id))

                elif role == 'physiotherapist':
                    cursor.execute('UPDATE Physiotherapist SET contact_number=%s, address=%s, email=%s WHERE physiotherapist_id=%s',
                                   (contact_number, address, email, user_id))

                elif role == 'admin':
                    cursor.execute('UPDATE Admin SET contact_number=%s, address=%s, email=%s WHERE admin_id=%s',
                                   (contact_number, address, email, user_id))

                # If a new file was uploaded, handle it
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                    # Update the profile image path in the corresponding table
                    if role == 'receptionist':
                        cursor.execute('UPDATE Receptionist SET profile_image=%s WHERE receptionist_id=%s', (filename, user_id))

                    elif role == 'physiotherapist':
                        cursor.execute('UPDATE Physiotherapist SET profile_image=%s WHERE physiotherapist_id=%s', (filename, user_id))

                    elif role == 'admin':
                        cursor.execute('UPDATE Admin SET profile_image=%s WHERE admin_id=%s', (filename, user_id))

                mysql.connection.commit()
                flash('Profile updated successfully!', 'success')

            except MySQLdb.Error as e:
                mysql.connection.rollback()
                flash(f'Error updating profile: {e}', 'error')
            finally:
                cursor.close()

            return redirect(url_for('profile'))  # Redirect to the profile page

        # If the request method is GET, fetch the user details for the edit form
        try:
            if role == 'receptionist':
                cursor.execute('SELECT * FROM Receptionist WHERE receptionist_id = %s', (user_id,))
            elif role == 'physiotherapist':
                cursor.execute('SELECT * FROM Physiotherapist WHERE physiotherapist_id = %s', (user_id,))
            elif role == 'admin':
                cursor.execute('SELECT * FROM Admin WHERE admin_id = %s', (user_id,))

            user = cursor.fetchone()
            if user:
                return render_template('update_details.html', user=user)  # Render edit form
            else:
                flash('User not found.', 'error')
                return redirect(url_for('profile'))  # Redirect to profile if user not found
        except MySQLdb.Error as e:
            flash(f'Error fetching user details: {e}', 'error')
            return redirect(url_for('profile'))
        finally:
            cursor.close()

    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('loginpage'))



@app.route('/change_password', methods=['POST'])
def change_password():
    if 'loggedin' in session:
        user_id = session['id']
        role = session['role']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('profile'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # Check current password
            if role == 'receptionist':
                cursor.execute('SELECT password FROM Receptionist_Login WHERE receptionist_id = %s', (user_id,))
            elif role == 'physiotherapist':
                cursor.execute('SELECT password FROM Physiotherapist_Login WHERE physiotherapist_id = %s', (user_id,))
            elif role == 'admin':
                cursor.execute('SELECT password FROM Admin_Login WHERE admin_id = %s', (user_id,))
            
            account = cursor.fetchone()
            
            # Verify current password using check_password_hash
            if account and check_password_hash(account['password'], current_password):
                # Update password using generate_password_hash
                hashed_new_password = generate_password_hash(new_password)

                if role == 'receptionist':
                    cursor.execute('UPDATE Receptionist_Login SET password = %s WHERE receptionist_id = %s', (hashed_new_password, user_id))
                elif role == 'physiotherapist':
                    cursor.execute('UPDATE Physiotherapist_Login SET password = %s WHERE physiotherapist_id = %s', (hashed_new_password, user_id))
                elif role == 'admin':
                    cursor.execute('UPDATE Admin_Login SET password = %s WHERE admin_id = %s', (hashed_new_password, user_id))
                
                mysql.connection.commit()
                flash('Password changed successfully!', 'success')
            else:
                flash('Current password is incorrect.', 'error')
        
        except MySQLdb.Error as e:
            flash(f'Error: {str(e)}', 'error')
        
        return redirect(url_for('profile'))
    flash('Unauthorized access!', 'error')
    return redirect(url_for('loginpage'))


@app.route('/logout')
def logout():
    if 'loggedin' in session:
        # Remove the user from the session
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('role', None)
        
        # Optionally, you can also flash a message to inform the user
        flash('You have been logged out successfully.', 'success')
        
        # Redirect to the login page
        return redirect(url_for('loginpage'))
    flash('You need to log in first to perform this action.', 'warning')
    return redirect(url_for('loginpage'))


@app.route('/admin_page')
def admin_page():
    if 'loggedin' in session and session['role'] == 'admin':
        user_name = session.get('user_name')
        return render_template('admin.html', user_name=user_name)
    flash('You need to log in as an admin to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/add_physio', methods=['POST'])
def add_physio():
    if 'loggedin' in session and session['role'] == 'admin':
        physio_name = request.form['physio_name']
        specialization = request.form['specialization']
        aadhar_number = request.form['aadhar_number']
        contact_number = request.form['contact_number']
        email = request.form['email']
        address = request.form['address']
        password = request.form.get('password', None) or str(session['id'])  # Default password is admin id
        
        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Handle file upload
        file = request.files.get('file')

        # Validate and save the uploaded file
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Get the secure filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Full path for saving
            file.save(file_path)  # Save the file to the path

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Use only the filename for the database
            cursor.execute('INSERT INTO Physiotherapist (physiotherapist_name, specialization, aadhar_number, contact_number, email, address, profile_image) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                           (physio_name, specialization, aadhar_number, contact_number, email, address, filename))
            physiotherapist_id = cursor.lastrowid
            cursor.execute('INSERT INTO Physiotherapist_Login (physiotherapist_id, password) VALUES (%s, %s)', (physiotherapist_id, hashed_password))
            mysql.connection.commit()
            flash('Physiotherapist added successfully!', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error adding physiotherapist: {e}', 'error')
        finally:
            cursor.close()
        
        return redirect(url_for('admin_page'))

    flash('You need to log in as an admin to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/remove_physio', methods=['POST'])
def remove_physio():
    if 'loggedin' in session and session['role'] == 'admin':
        physiotherapist_id = request.form['physiotherapist_id']
        
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Delete from Physiotherapist_Login table first
            cursor.execute('DELETE FROM Physiotherapist_Login WHERE physiotherapist_id = %s', (physiotherapist_id,))
            # Then delete from Physiotherapist table
            cursor.execute('DELETE FROM Physiotherapist WHERE physiotherapist_id = %s', (physiotherapist_id,))
            mysql.connection.commit()
            flash('Physiotherapist removed successfully!', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error removing physiotherapist: {e}', 'error')
        finally:
            cursor.close()
        
        return redirect(url_for('admin_page'))
    
    flash('You need to log in as an admin to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/add_receptionist', methods=['POST'])
def add_receptionist():
    if 'loggedin' in session and session['role'] == 'admin':
        receptionist_name = request.form['receptionist_name']
        contact_number = request.form['contact_number']
        address = request.form['address']
        aadhar_number = request.form['aadhar_number']
        email = request.form['email']
        password = request.form.get('password', None) or str(session['id'])  # Default password is admin id

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Handle file upload
        file = request.files.get('file')  # Change 'file' to the name of your file input field in the form

        # Validate and save the uploaded file
        file_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('INSERT INTO Receptionist (receptionist_name, contact_number, address, aadhar_number, email, image_path) VALUES (%s, %s, %s, %s, %s, %s)',
                           (receptionist_name, contact_number, address, aadhar_number, email, file_path))
            receptionist_id = cursor.lastrowid
            cursor.execute('INSERT INTO Receptionist_Login (receptionist_id, password) VALUES (%s, %s)', (receptionist_id, hashed_password))
            mysql.connection.commit()
            flash('Receptionist added successfully!', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error adding receptionist: {e}', 'error')
        finally:
            cursor.close()
        
        return redirect(url_for('admin_page'))

    flash('You need to log in as an admin to perform this action.', 'warning')
    return redirect(url_for('loginpage'))
@app.route('/remove_receptionist', methods=['POST'])
def remove_receptionist():
    if 'loggedin' in session and session['role'] == 'admin':
        receptionist_id = request.form['receptionist_id']
        
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Delete the receptionist from the Receptionist_Login table first
            cursor.execute('DELETE FROM Receptionist_Login WHERE receptionist_id = %s', (receptionist_id,))
            # Then delete the receptionist from the Receptionist table
            cursor.execute('DELETE FROM Receptionist WHERE receptionist_id = %s', (receptionist_id,))
            mysql.connection.commit()
            flash('Receptionist removed successfully!', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error removing receptionist: {e}', 'error')
        finally:
            cursor.close()
        
        return redirect(url_for('admin_page'))
    
    flash('You need to log in as an admin to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/add_admin', methods=['POST'])
def add_admin():
    if 'loggedin' in session and session['role'] == 'admin':
        admin_name = request.form['admin_name']
        aadhar_number = request.form['aadhar_number']
        contact_number = request.form['contact_number']
        email = request.form['email']
        address = request.form['address']
        password = request.form.get('password', None) or str(session['id'])  # Default password is admin id
        
        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Handle image file upload
        file = request.files.get('file')  # 'file' corresponds to the name of the input field in the form

        # Validate and save the uploaded file
        file_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('INSERT INTO Admin (admin_name, aadhar_number, contact_number, email, address, image_path) VALUES (%s, %s, %s, %s, %s, %s)',
                           (admin_name, aadhar_number, contact_number, email, address, file_path))
            admin_id = cursor.lastrowid
            cursor.execute('INSERT INTO Admin_Login (admin_id, password) VALUES (%s, %s)', (admin_id, hashed_password))
            mysql.connection.commit()
            flash('Admin added successfully!', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error adding admin: {e}', 'error')
        finally:
            cursor.close()
        
        return redirect(url_for('admin_page'))

    flash('You need to log in as an admin to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/remove_admin', methods=['POST'])
def remove_admin():
    if 'loggedin' in session and session['role'] == 'admin':
        admin_id = request.form['admin_id']
        
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Delete from Admin_Login table first
            cursor.execute('DELETE FROM Admin_Login WHERE admin_id = %s', (admin_id,))
            # Then delete from Admin table
            cursor.execute('DELETE FROM Admin WHERE admin_id = %s', (admin_id,))
            mysql.connection.commit()
            flash('Admin removed successfully!', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error removing admin: {e}', 'error')
        finally:
            cursor.close()
        
        return redirect(url_for('admin_page'))
    
    flash('You need to log in as an admin to perform this action.', 'warning')
    return redirect(url_for('loginpage'))
@app.route('/view_physios')
def view_physios():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Physiotherapist')
        physiotherapists = cursor.fetchall()
        return render_template('view_physios.html', physiotherapists=physiotherapists)
    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/view_recepts')
def view_recept():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Receptionist')
        receptionists = cursor.fetchall()
        return render_template('view_recepts.html', receptionists=receptionists)
    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('loginpage'))


@app.route('/receptionist_page')
def receptionist_page():
    if 'loggedin' in session and session['role'] in ['receptionist', 'admin']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        user_name = session.get('user_name')
        return render_template('receptionist.html', user_name=user_name)
    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/physiotherapist_page')
def physiotherapist_page():
    if 'loggedin' in session and session['role'] == 'physiotherapist':
        user_name = session.get('user_name')
        return render_template('physiotherapist.html', user_name=user_name)
    flash('You need to log in as physiotherapist to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/add_patient', methods=['POST'])
def add_patient():
    if 'loggedin' in session and session['role'] in ['receptionist', 'admin']:
        patient_name = request.form['patientName']
        age = request.form['patientAge']
        sex = request.form['patientSex']
        physiotherapist_name = request.form['physiotherapistName']
        address = request.form['address']
        contact_number = request.form['contactNumber']
        email = request.form['email']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Patient (patient_name, age, sex, physiotherapist_name, address, contact_number, email) VALUES (%s, %s, %s, %s, %s, %s, %s)', (patient_name, age, sex, physiotherapist_name, address, contact_number, email))
        mysql.connection.commit()
        flash('Patient added successfully!', 'success')
        return redirect(url_for('receptionist_page'))
    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('loginpage'))

@app.route('/search_patient', methods=['POST'])
def search_patient():
    if 'loggedin' in session and session['role'] in ['receptionist', 'admin']:
        start_date = request.form['startDate']
        end_date = request.form['endDate']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Patient WHERE datetime BETWEEN %s AND %s', (start_date, end_date))
        patients = cursor.fetchall()
        return render_template('search_results.html', patients=patients)
    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('login'))
@app.route('/patient_history', methods=['POST'])
def patient_history():
    if 'loggedin' in session and session['role'] in ['receptionist', 'physiotherapist', 'admin']:
        patient_name = request.form.get('patient_name', '').strip()
        patient_id = request.form.get('patient_id', '').strip()
        contact_number = request.form.get('mobile_no', '').strip()  # Updated to match the column name
        email = request.form.get('email', '').strip()

        # Ensure at least one field is provided
        if not any([patient_name, patient_id, contact_number, email]):
            flash('Please provide at least one search criterion (name, ID, contact number, or email).', 'error')
            return redirect(url_for('receptionist_page') if session['role'] == 'receptionist' else url_for('physiotherapist_page'))

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query = 'SELECT * FROM Patient WHERE 1'
            query_params = []

            # Build query dynamically based on provided inputs
            if patient_name:
                query += ' AND patient_name = %s'
                query_params.append(patient_name)
            if patient_id:
                query += ' AND patient_id = %s'
                query_params.append(patient_id)
            if contact_number:
                query += ' AND contact_number = %s'  # Updated column name
                query_params.append(contact_number)
            if email:
                query += ' AND email = %s'
                query_params.append(email)

            cursor.execute(query, tuple(query_params))
            patients = cursor.fetchall()

            if patients:
                patient_treatments = {}
                for patient in patients:
                    patient_id = patient['patient_id']
                    cursor.execute('SELECT * FROM Treatment WHERE patient_id = %s', (patient_id,))
                    treatments = cursor.fetchall()
                    patient_treatments[patient_id] = {'patient': patient, 'treatments': treatments}

                return render_template('patient_history.html', patient_treatments=patient_treatments)
            else:
                flash('No patient found with the provided details.', 'error')
        
        except MySQLdb.Error as e:
            flash(f'Error: {str(e)}', 'error')
        except Exception as e:
            flash(f'An unexpected error occurred: {str(e)}', 'error')
        
        return redirect(url_for('receptionist_page') if session['role'] == 'receptionist' else url_for('physiotherapist_page'))

    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('login'))



@app.route('/physiotherapist_patients', methods=['POST'])
def physiotherapist_patients():
    if 'loggedin' in session and session['role'] in ['receptionist', 'admin']:
        physiotherapist_name = request.form['physiotherapistName']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Patient WHERE physiotherapist_name = %s', (physiotherapist_name,))
        patients = cursor.fetchall()
        return render_template('physiotherapist_patients.html', patients=patients)
    flash('You need to log in to perform this action.', 'warning')
    return redirect(url_for('login'))

@app.route('/add_treatment', methods=['POST'])
def add_treatment():
    if 'loggedin' in session and session['role'] == 'physiotherapist':
        if request.method == 'POST':
            patient_id = request.form['patientId']
            diagnosis = request.form['diagnosis']
            treatment = request.form['treatment']
            physiotherapist_id = session.get('id')  # Assuming physiotherapist_id is stored in the session

            print(f"patient_id: {patient_id}, diagnosis: {diagnosis}, treatment: {treatment}, physiotherapist_id: {physiotherapist_id}")

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Check if the patient exists
            cursor.execute('SELECT * FROM Patient WHERE patient_id = %s', (patient_id,))
            patient = cursor.fetchone()
            
            if patient:
                try:
                    cursor.execute('INSERT INTO Treatment (physiotherapist_id, patient_id, diagnosis, treatment) VALUES (%s, %s, %s, %s)', (physiotherapist_id, patient_id, diagnosis, treatment))
                    mysql.connection.commit()
                    flash('Treatment details added successfully!', 'success')
                except MySQLdb.IntegrityError as e:
                    print(f"Error inserting data: {e}")
                    flash(f'Error inserting data: {e}', 'error')
            else:
                flash('Error: Patient ID does not exist.', 'error')
            
            cursor.close()
            return redirect(url_for('physiotherapist_page'))

        return render_template('physiotherapist.html')
    flash('You need to log in as physiotherapist to perform this action.', 'warning')
    return redirect(url_for('loginpage'))
    


if __name__ == '__main__':
    app.run(debug=True)
