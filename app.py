import os
import sqlite3
from flask import Flask, render_template,flash,session,request,redirect, url_for

app = Flask(__name__,static_url_path='/static')
app.secret_key="123"

sqlconnection =sqlite3.connect("admin.db")
sqlconnection.execute("create table if not exists users(id integer primary key,username text,password text, email text)")
sqlconnection.execute("create table if not exists admin(username text,password text, email text)")
sqlconnection.execute("create table if not exists stationary(id integer primary key,sname text,cost integer, image blob,image_url text)")
sqlconnection.execute("create table if not exists book(id integer primary key,bname text,cost integer, image blob,image_url text)")
sqlconnection.execute(('''CREATE TABLE IF NOT EXISTS feed(name TEXT, email TEXT, feedback TEXT)'''))
sqlconnection.close()

@app.route('/')
def welcome():
    return render_template('welcome.html')

def fetch_books():
    connection = sqlite3.connect('admin.db')
    cursor = connection.cursor()
    cursor.execute("SELECT bname,cost,image FROM book")
    books = cursor.fetchall()
    connection.close()
    return books

@app.route('/home')
def Home():
    return render_template('home.html',)

@app.route('/Books')
def Books():
    books = fetch_books()
    return render_template('books.html', books=books)

def fetch_stationarys():
    connection = sqlite3.connect('admin.db')
    cursor = connection.cursor()
    cursor.execute("SELECT sname, cost, image FROM stationary")
    stationarys = cursor.fetchall()
    connection.close()
    return stationarys

@app.route('/Stationary')
def stationarys():
    stationarys = fetch_stationarys()
    return render_template('Stationary.html', stationarys=stationarys)

@app.route('/submit_feedback', methods=['POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['mail']
        feedback = request.form['feedback']

        conn = sqlite3.connect('admin.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO feed (name, email, feedback) VALUES (?, ?, ?)", (name, email, feedback))
        conn.commit()
        conn.close()

        return redirect('/')
    else:
        return 'Error'


@app.route('/Contact')
def Contact():
    return render_template('Contact.html')


@app.route('/Chatbot')
def Chatbot():
    return render_template('Chatbot.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register',methods=["GET","POST"])
def register():
 if request.method =="POST":
        try:
            name=request.form['username']
            psswd=request.form['password']
            mail=request.form['email']
            sqlconnection=sqlite3.connect('admin.db')
            cur=sqlconnection.cursor()
            cur.execute("insert into users(username,password,email)values(?,?,?)",(name,psswd,mail))
            sqlconnection.commit()
            flash("Record added Successfully","success")
        except:
            flash("Error in Insert Operation","danger")
        finally:   
           return redirect('/login')
           sqlconnection.close()


 return render_template("register.html")

@app.route('/log',methods =["GET","POST"])
def log():
    if request.method =="POST":
        name=request.form['username']
        psswd=request.form['password']
        sqlconnection= sqlite3.connect('admin.db')
        sqlconnection.row_factory=sqlite3.Row
        cur=sqlconnection.cursor()
        
        cur.execute("select * from users where username =? and password =?",(name,psswd))
        data=cur.fetchone()
        if (data):
          session['name']=data["username"] 
          session['password']=data["password"] 
          flash("Welcome to HVK ","logged")
          return redirect("/")
        else:
            flash("Invalid Username and Password","danger")
            return redirect('/login')
    return redirect('/')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/adminlogin',methods =["GET","POST"])
def adminlogin():
    if request.method =="POST":
        name=request.form['username']
        psswd=request.form['password']
        sqlconnection= sqlite3.connect('admin.db')
        sqlconnection.row_factory=sqlite3.Row
        cur=sqlconnection.cursor()
        
        cur.execute("select * from admin where username =? and password =?",(name,psswd))
        data=cur.fetchone()
        if (data):
          session['name']=data["username"] 
          session['password']=data["password"] 
          flash("Welcome to HVK  ","logged")
          return redirect("/adminhome")
        else:
            flash("Invalid Username and Password","danger")
            return redirect('/adminlogin')
    return redirect('/adminhome')

@app.route('/adminhome')
def adminhome():
    return render_template('adminhome.html')

@app.route('/abooks')
def abook():
    books = fetch_books()
    return render_template('abooks.html', books=books)

@app.route('/astationary')
def astationary():
    stationarys = fetch_stationarys()
    return render_template('aStationary.html', stationarys=stationarys)

@app.route('/addsta')
def admin_dashboards():
    return render_template('addsta.html')

@app.route('/addsta', methods=['POST'])
def add_stationary():
    if request.method == 'POST':
        sname = request.form['Name']
        cost = request.form['Cost']
        image = request.files['image']
        
        # Ensure the upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the image to the upload directory
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))

        image_url = url_for('static', filename="uploads"+image.filename)
        # Insert book data into the database
        connection = sqlite3.connect('admin.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO stationary (sname, cost, image,image_url) VALUES (?, ?, ?,?)", (sname, cost, image.filename,image_url))
        connection.commit()
        connection.close()

    return redirect(url_for('astationary'))

@app.route('/aorders')
def aorders():
    return render_template('aorders.html')

@app.route('/afeedback')
def afeedback():
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, feedback FROM feed")
    feedback_data = cursor.fetchall()
    conn.close()
    return render_template('afeedback.html', feedback_data=feedback_data)

def connect_db():
    return sqlite3.connect('admin.db')

@app.route('/acustomers')
def customers():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('acustomers.html', users=users)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/AddBook')
def admin_dashboard():
    return render_template('addbook.html')




# Route to handle form submission for adding a new book
@app.route('/Addbook', methods=['POST'])
def add_book():
    if request.method == 'POST':
        bname = request.form['Name']
        cost = request.form['Cost']
        image = request.files['image']
        
        # Ensure the upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the image to the upload directory
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))

        image_url = url_for('static', filename="uploads"+image.filename)
        # Insert book data into the database
        connection = sqlite3.connect('admin.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO book (bname, cost, image,image_url) VALUES (?, ?, ?,?)", (bname, cost, image.filename,image_url))
        connection.commit()
        connection.close()

    return redirect(url_for('abook'))

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/Cart')
def cart():
    return render_template('cart.html')

def connect_db():
    return sqlite3.connect('admin.db')

# Create a function to initialize the database tables
def init_db():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    zipcode TEXT
                )''')
    conn.commit()
    conn.close()

# Initialize the database tables when the app starts
init_db()

# Route to render the checkout page
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

# Route to handle the checkout form submission
@app.route('/checkout', methods=['POST'])
def process_checkout():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        zipcode = request.form['zipcode']

        # Save form data to the database
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO orders (name, email, phone, address, zipcode) VALUES (?, ?, ?, ?, ?)",
                    (name, email, phone, address, zipcode))
        conn.commit()
        conn.close()

        return redirect('/thankyou')  # Redirect to a thank you page after successful submission

# Define a route for the thank you page
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

    

if __name__ == '__main__':
    app.run(debug=True)
