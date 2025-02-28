from flask import Flask, redirect, render_template, url_for, request, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask import session as login_session
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy import select
from datetime import datetime as dt
import os



app=Flask(__name__,  static_folder='static')
app.secret_key = "dandandakndalkd"

login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\269092\\Downloads\\SQLiteDatabaseBrowserPortable\\site.db'

app.config['SECRET_KEY'] = 'this is a secret key '
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
login_manager.init_app(app)


UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER






class User(db.Model, UserMixin):
    __tablename__= "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
def __repr__(self):
    return f'<User {self.username}>'

class Menu(db.Model):
    __tablename__="menu"
    food_id= db.Column(db.Integer, primary_key=True)
    food_name= db.Column(db.String(50))
    price= db.Column(db.Numeric(10,2), nullable=False)
    food_description = db.Column(db.String(200))
    food_image= db.Column(db.String(200))
    basketitems = relationship("Basket", back_populates="menu")

def __unicode__(self):
    return f'<Menu {self.food_name}>'

class Basket(db.Model):
    __tablename__ = "basket"
    basket_id = db.Column(db.Integer, primary_key=True)
    basket_name = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=False)
    # adding the foreign key
    food_id = db.Column(db.Integer, db.ForeignKey('menu.food_id'), nullable=False)
    menu = relationship("Menu", back_populates="basketitems")  # 2nd backpopulates method

    # def __repr__(self):

def __unicode__(self):  # new line
    return f'<CartI'
    f'tem {self.cart_name}>'


class Customer(db.Model, UserMixin):
    __tablename__= "customer"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
def __repr__(self):
    return f'<Customer {self.username}>'

class Order(db.Model):
    __tablename__ = "order"
    order_no = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique primary key
    food_id = db.Column(db.Integer, nullable=False)  # Correcting syntax for food_id
    quantity = db.Column(db.Integer, nullable=False)
    pay_order_no = db.Column(db.Integer, db.ForeignKey('pay.order_no'), nullable=True)  # Foreign key to Pay table

    pay_reference = db.relationship("Pay", back_populates="orders")  # Define relationship back to Pay

    def __repr__(self):
        return f'<Order {self.order_no}>'

class Pay(db.Model):
    __tablename__ = "pay"
    pay_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.Integer, unique=True)  # Foreign key target column in Pay

    total_price = db.Column(db.Numeric(10, 2))
    cust_name = db.Column(db.String(30), nullable=False)
    cust_address = db.Column(db.String(30), nullable=False)
    cust_postcode = db.Column(db.String(30), nullable=False)
    cust_email = db.Column(db.String(30), nullable=False)
    cust_cardno = db.Column(db.String(30), nullable=False)
    card_expirydate = db.Column(db.String(30), nullable=False)
    card_cvv = db.Column(db.String(30), nullable=False)
    trans_option = db.Column(db.String(30))
    pay_datetime = db.Column(db.DateTime, default=dt.now)

    orders = db.relationship("Order", back_populates="pay_reference")  # Relationship to Order



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def homepage():
   menu= db.session.query(Menu).all()
   return render_template("index.html", menu=menu)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')

        checkemail = User.query.filter(User.email == email).first()
        checkuser = User.query.filter(User.username == username).first()

        if checkemail != None:
            flash("Please register using a different email.")

            return render_template("register.html")
        elif checkuser is not None:
            flash("Username already exists !")

            return render_template("register.html")

        else:
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            #db.session["username"] = username
            login_session['username'] = username
            login_user(user)
            return redirect(url_for('welcome'))
        else:
            #if "username" in db.session:
            if "username" in login_session:
                return redirect(url_for('welcome'))

    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if "username" in login_session:
        username = login_session['username']
        food = db.session.query(Menu).all()
        #path=food.file_image
        return render_template('index.html', food=food)
    else:
        return redirect(url_for('login'))


@app.route('/addfood', methods=['GET', 'POST'])
def addfood():
    if request.method == 'POST':
        print("addfood")
        food_name = request.form['food_name']
        food_price = float(request.form['food_price'])
        food_type = request.form['food_type']

        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        #comment the following 2 lines
        #return path
        #return 'ok'
        new_food = Menu(food_name=food_name, price=food_price, food_description=food_type, food_image=path)
        db.session.add(new_food)
        db.session.commit()

        return redirect(url_for('welcome'))
    else:
        print("addfood")
    return render_template('createfood.html')

if __name__ == "__main__":
    #app_dir = op.realpath(os.path.dirname(__file__))
    with app.app_context():
        db.create_all()
        # export_to_xml()
    app.run(debug=True)

