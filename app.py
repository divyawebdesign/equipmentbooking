from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'divya'
app.config['MYSQL_PASSWORD'] = 'Strong!password'  
app.config['MYSQL_DB'] = 'equipment'

mysql = MySQL(app)

@app.route('/')
def home():
    return redirect(url_for('render_login_page'))



@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'GET':
        return render_template('admin_signup.html')
    else:
        admin_id = request.form['adminID']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        name = request.form['name']

        if not admin_id or not password or not name:
            return "All fields are required!", 400

        if password != confirm_password:
            return "Passwords do not match!", 400

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO admin (adminID, password, name) VALUES (%s, %s, %s)",
                        (admin_id, password, name))
            mysql.connection.commit()
            cur.close()
            return "Signup successful! <a href='/admin_login.html'>Login now</a>"
        except Exception as e:
            return f"Database error: {str(e)}", 500

@app.route('/admin_login', methods=['POST'])
def admin_login():
    admin_id = request.form['adminID']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admin WHERE adminID = %s AND password = %s", (admin_id, password))
    admin = cur.fetchone()
    cur.close()

    if admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return "Login failed. <a href='/admin_signup'>Sign up here</a>"

@app.route('/admin_login.html')
def render_login_page():
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipment")
    equipment_list = cur.fetchall()
    cur.close()
    return render_template('admin_dashboard.html', equipment_list=equipment_list, admin_name="Admin")


@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'GET':
        return render_template('add_equipment.html')
    else:
        equipment_name = request.form['equipmentName']
        description = request.form['description']
        quantity = request.form['quantity']
        category = request.form['category']
        status = request.form['status']

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO equipment (name, description, quantity, category, status) VALUES (%s, %s, %s, %s, %s)",
                (equipment_name, description, quantity, category, status)
            )
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            return f"Database error: {str(e)}", 500

@app.route('/delete_equipment', methods=['GET', 'POST'])
def delete_equipment():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipment")
    equipment_list = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        equipment_id = request.form['equipment_id']
        try:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM equipment WHERE id = %s", (equipment_id,))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('delete_equipment'))
        except Exception as e:
            return f"Database error: {str(e)}", 500

    return render_template('delete_equipment.html', equipment_list=equipment_list)

@app.route('/update_equipment')
def update_equipment():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipment")
    equipment_list = cur.fetchall()
    cur.close()
    return render_template('update-equipment.html', equipment_list=equipment_list)

@app.route('/edit_equipment/<int:equipment_id>', methods=['GET', 'POST'])
def edit_equipment(equipment_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipment WHERE id = %s", (equipment_id,))
    equipment = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        equipment_name = request.form['equipmentName']
        description = request.form['description']
        quantity = request.form['quantity']
        category = request.form['category']
        status = request.form['status']

        try:
            cur = mysql.connection.cursor()
            cur.execute(""" 
                UPDATE equipment 
                SET name = %s, description = %s, quantity = %s, category = %s, status = %s
                WHERE id = %s
            """, (equipment_name, description, quantity, category, status, equipment_id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            return f"Error: {str(e)}", 500

    return render_template('edit-equipment.html', equipment=equipment)



@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'GET':
        return render_template('user_signup.html')
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        phone = request.form['phone']
        gender = request.form['gender']

        if not name or not email or not password or not phone or not gender:
            return "All fields are required!", 400

        if password != confirm_password:
            return "Passwords do not match!", 400

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password, phone, gender) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, password, phone, gender))
            mysql.connection.commit()
            cur.close()
            return '''
                <script>
                    alert("Signup successful!");
                    window.location.href = "/user_login.html";
                </script>
            '''
        except Exception as e:
            return f"Database error: {str(e)}", 500

@app.route('/user_login', methods=['POST'])
def user_login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user:
        return redirect(url_for('user_dashboard', username=user[1], user_id=user[0]))  
    else:
        return "Login failed. <a href='/user_signup'>Sign up here</a>"

@app.route('/user_login.html')
def render_user_login_page():
    return render_template('user_login.html')

@app.route('/user_dashboard/<username>')
def user_dashboard(username):
    category = request.args.get('category', 'all')  

    cur = mysql.connection.cursor()
    if category == 'all':
        cur.execute("SELECT * FROM equipment")
    else:
        cur.execute("SELECT * FROM equipment WHERE category = %s", (category,))
        
    equipment_list = cur.fetchall()
    cur.close()

    return render_template('user-dashboard.html', username=username, equipment_list=equipment_list, selected_category=category)


@app.route('/book_equipment', methods=['POST'])
def book_equipment():
    user_id = request.form['user_id']
    equipment_id = request.form['equipment_id']

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO book (UserID, EquipmentID) VALUES (%s, %s)", (user_id, equipment_id))  # Keep UserID
        mysql.connection.commit()
        cur.close()
        
        return '''
            <script>
                alert("Booking request submitted successfully!");
                // No redirect; keep the user on the same page
            </script>
        '''
    except Exception as e:
        return f"Database error: {str(e)}", 500



if __name__ == '__main__':
    app.run(debug=True)
