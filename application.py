from flask import Flask, request, render_template, url_for, flash, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import pandas as pd

app=Flask(__name__)

app.config['SECRET_KEY']='uOzPG137aJNoq2bBJ4b9P81DY5vCiRXj'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db_billing.db'
db=SQLAlchemy(app)	

class User(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(25), nullable=False)
	surname=db.Column(db.String(25), nullable=False)
	username=db.Column(db.String(13),nullable=False)
	password=db.Column(db.String(13),nullable=False)

class Receipt(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	customer_id=db.Column(db.Integer, db.ForeignKey('customer.id'))
	payment_id=db.Column(db.Integer, db.ForeignKey('payment.id'))
	date_issue=db.Column(db.DateTime, nullable=False)
	total=db.Column(db.Numeric, nullable=False)

class Payment(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	#receipt_id=db.Column(db.Integer, db.ForeignKey('receipt.id'))
	receipt=db.relationship('Receipt',backref='payment')

class Customer(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(25), nullable=False)
	surname=db.Column(db.String(25), nullable=False)
	tax_code=db.Column(db.String(16), nullable=False)
	course_id=db.Column(db.Integer)
	receipts=db.relationship('Receipt',backref='customer', lazy=True)

@app.route('/',methods=['GET','POST'])
def index():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if not username:
			flash('username obbligatorio!')
		elif not password:
			flash('password obbligatoria!')
		else:
			user=User.query.filter_by(username=username, password=password).first()
			if user:
				return render_template('search.html')
		flash('Utente non trovato. Verifica le tue credenziali')
		return render_template('index.html')
	else:
		return render_template('index.html')

@app.route('/payment',methods=['GET','POST'])
def add_payment(customer_id):
	if request.method == 'POST':
		x=customer_id
	else:
		customer_id=1	
	return render_template('add_payment.html', customer_id=customer_id)

@app.route('/search', methods=['GET','POST'])
def search():
	return render_template('search.html')



#API
@app.route('/adduser', methods=['GET','POST'])
def add_user():
	if request.method == 'POST':
		name=request.form['name']
		surname=request.form['surname']
		username=request.form['username']
		password=request.form['password']
		repeatpassword=request.form['repeatpassword']
		if not username:
			flash('username obbligatorio!')
		elif not password:
			flash('password obbligatoria!')
		elif not name:
			flash('nome obbligatorio!')
		elif not surname:
			flash('cognome obbligatorio!')
		elif password!=repeatpassword:
			flash('le password non corrispondono!')
		else:
			checkuser=User.query.filter_by(username=username).first()
			if checkuser:
				flash('Utente gia'' presente')
			user=User(
				name=name,
				surname=surname,
				username=username, 
				password=password)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('index'))
		return render_template('newuser.html') #I land again on newuser page if conditions are not all ok
	else:
		return render_template('newuser.html')


#===================== test Export DB in Excel =====================

UPLOAD_FOLDER = 'C:/Users/casa/Downloads'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

def to_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict


@app.route('/excel', methods=['GET', 'POST'])
def exportexcel():
    data = User.query.all()
    data_list = [to_dict(item) for item in data]
    df = pd.DataFrame(data_list)
    filename = app.config['UPLOAD_FOLDER']+"/userlist.xlsx"
    print("Filename: "+ filename)

    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, sheet_name='kaz01')
    writer.save()

    return redirect(url_for('add_user'))

