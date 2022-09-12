from flask import Flask, request, render_template, url_for, flash, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import pandas as pd
import openpyxl
import os

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
	payments=db.relationship('Payment', backref='user')

class Receipt(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	customer_id=db.Column(db.Integer, db.ForeignKey('customer.id'))
	payment_id=db.Column(db.Integer, db.ForeignKey('payment.id'))
	date_issue=db.Column(db.DateTime, nullable=False)
	total=db.Column(db.Numeric, nullable=False)

class Payment(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	cash001=db.Column(db.Integer)
	cash002=db.Column(db.Integer)
	cash005=db.Column(db.Integer)
	cash010=db.Column(db.Integer)
	cash020=db.Column(db.Integer)
	cash050=db.Column(db.Integer)
	cash100=db.Column(db.Integer)
	cash200=db.Column(db.Integer)
	payd_card=db.Column(db.Integer)
	type_card=db.Column(db.String)
	payd_bank=db.Column(db.Integer)
	customer_id=db.Column(db.Integer, db.ForeignKey('customer.id'))
	receipt=db.relationship('Receipt',backref='payment')
	user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

class Customer(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(25), nullable=False)
	surname=db.Column(db.String(25), nullable=False)
	tax_code=db.Column(db.String(16), nullable=False)
	address=db.Column(db.String(40))
	zip_code=db.Column(db.String(10))
	city=db.Column(db.String(25))
	prov_state=db.Column(db.String(2))
	nation=db.Column(db.String)
	course_id=db.Column(db.Integer)
	receipts=db.relationship('Receipt',backref='customer', lazy=True)
	payments=db.relationship('Payment',backref='customer')

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
				return redirect(url_for('list_students'))
		flash('Utente non trovato. Verifica le tue credenziali')
		return render_template('index.html')
	else:
		return render_template('index.html')

@app.route('/addpayment/<customer_id>',methods=['GET','POST'])
def add_payment(customer_id):
	if request.method == 'POST':
		x=1
	else:
		print("customer id: " + customer_id)
		return render_template('newpayment.html',customer_id=customer_id)

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

UPLOAD_FOLDER = 'D:/Luka/Programming/Python/WebCash/Downloads'
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

    writer = pd.ExcelWriter(filename, engine='openpyxl')
    df.to_excel(writer, sheet_name='kaz01')
    writer.save()

    return redirect(url_for('add_user'))


#https://www.tutorialexample.com/python-pandas-append-data-to-excel-a-step-guide-python-pandas-tutorial/
@app.route('/newrow', methods=['GET','POST'])
def new_row():
	
	#excel_name = app.config['UPLOAD_FOLDER']+"/userlist03.xlsx"
	excel_name ='/Downloads/userlist.xlsx'

	data=User.query.order_by(User.id.desc()).first()
	data_list = [to_dict(data)]
	df = pd.DataFrame(data_list, index= None)
	
	df_source = None
	if os.path.exists(excel_name):
		data_list=pd.read_excel('/Downloads/userlist.xlsx',engine='openpyxl',index_col=None)
		df_source = pd.DataFrame(data_list)
	if df_source is not None:
		df_dest = df_source.append(df)
	else:
		df_dest = df

	writer=pd.ExcelWriter(excel_name)
	df_dest.to_excel(writer, sheet_name='kaz02')
	writer.save()

	return redirect(url_for('add_user'))

@app.route('/addcustomer', methods=['GET','POST'])
def add_customer():
	if request.method=='POST':
		name=request.form['name']
		surname=request.form['surname']
		tax_code=request.form['tax_code']
		address=request.form['address']
		zip_code=request.form['zip_code']
		city=request.form['city']
		prov_state=request.form['prov_state']
		nation=request.form['nation']
		course_id=request.form['course_id']
		customer=Customer(name=name, surname=surname, tax_code=tax_code,address=address,zip_code=zip_code,city=city, prov_state=prov_state,nation=nation, course_id=course_id)
		db.session.add(customer)
		db.session.commit()
		
		#customers=Customer.query.all()
		#return render_template('liststudents.html', customers=customers)
		return redirect(url_for('list_students'))

	else:
		return render_template('newcustomer.html')

@app.route('/liststudents')
def list_students():
	customers=Customer.query.all()
	return render_template('liststudents.html', customers=customers)