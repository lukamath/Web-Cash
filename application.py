from flask import Flask, request, render_template, url_for, flash, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_session import Session
from datetime import date, datetime
import pandas as pd
import openpyxl
import os

app=Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
	description=db.Column(db.String)

class Payment(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	total=db.Column(db.Numeric, nullable=False)
	paym_card=db.Column(db.Integer)
	type_card=db.Column(db.String)
	paym_bank=db.Column(db.Integer)
	customer_id=db.Column(db.Integer, db.ForeignKey('customer.id'))
	receipt=db.relationship('Receipt',backref='payment')
	cash=db.relationship('Cash',backref='payment')
	user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

class Cash(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	date_collection=db.Column(db.DateTime, nullable=False)
	cash001=db.Column(db.Integer)
	cash002=db.Column(db.Integer)
	cash005=db.Column(db.Integer)
	cash010=db.Column(db.Integer)
	cash020=db.Column(db.Integer)
	cash050=db.Column(db.Integer)
	cash100=db.Column(db.Integer)
	cash200=db.Column(db.Integer)
	vault=db.Column(db.Integer)  	#for user cash sheet
	deposit=db.Column(db.Integer)	#for admin withdraw
	payment_id=db.Column(db.Integer, db.ForeignKey('payment.id'))
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
				session["user"] = username
				session["user_id"] = user.id
				return redirect(url_for('list_students'))
		flash('Utente non trovato. Verifica le tue credenziali')
		return render_template('index.html')
	else:
		return render_template('index.html')

@app.route('/addpayment/<customer_id>',methods=['GET','POST'])
def add_payment(customer_id):
	customer=Customer.query.filter_by(id=customer_id).first()
	payments=Payment.query.filter_by(customer_id=customer_id).all()
	if request.method == 'POST':
		description=request.form['description']
		payment_method=request.form['payment-method']
		payment_quote=request.form['payment-quote']
		if not description:
			flash('description obbligatorio!')
		elif not payment_method:
			flash('payment-method obbligatoria!')
		elif not payment_quote:
			flash('payment-quote obbligatorio!')
		else:

			if payment_method=='Contante':
				#add_cash(payment, payments, receipt, customer)
				return redirect(url_for('add_cash', 
					customer_id=customer_id,
					description=description, 
					payment_method=payment_method, 
					payment_quote=payment_quote))

			else:	
				flash('sono fuori da add cash e dentro else --> GRAVISSIMO')
				flash('payment_method: '+ payment_method)				
				payments=Payment.query.filter_by(customer_id=customer_id).all()
				return render_template('liststudentspayments.html',customer=customer,payments=payments)
	else:
		print("customer id: " + customer_id)
		return render_template('liststudentspayments.html',customer=customer,payments=payments)


@app.route('/addcash',methods=['GET','POST'])
def add_cash():
	customer_id  = request.args.get('customer_id', None)
	description  = request.args.get('description', None)
	payment_method  = request.args.get('payment_method', None)
	payment_quote  = request.args.get('payment_quote', None)
	customer=Customer.query.filter_by(id=customer_id).first() #da rivedere se conviene rifare la query

	if request.method=='POST':

		payment=Payment(
				total=payment_quote,
				type_card=payment_method,
				customer_id=customer_id,
				user_id=session.get('user')
				)
		db.session.add(payment)
		db.session.commit()

		receipt=Receipt(
					customer_id=payment.customer_id,
					payment_id=payment.id,
					date_issue=date.today(),
					description=description
			)
		db.session.add(receipt)
		db.session.commit()

		customer=Customer.query.filter_by(id=customer_id).first()
		payments=Payment.query.filter_by(customer_id=customer_id).all()

		print('add pieces of cash here -->' + str(session.get('user_id')) + " - " + session.get('user') + " --> payment id: " + str(payment_quote))

		cash001 = request.form['cash001']
		cash002 = request.form['cash002']
		cash005 = request.form['cash005']
		cash010 = request.form['cash010']
		cash020 = request.form['cash020']
		cash050 = request.form['cash050']
		cash100 = request.form['cash100']
		cash200 = request.form['cash200']
		vault=0
		deposit=0
		payment_id=payment.id
		user_id=session.get('user_id')
		cash=Cash(
			date_collection=date.today(),
			cash001=cash001,
			cash002=cash002,
			cash005=cash005,
			cash010=cash010,
			cash020=cash020,
			cash050=cash050,
			cash100=cash100,
			cash200=cash200,
			vault=vault,
			deposit=deposit,
			payment_id=payment_id,
			user_id=user_id
			)
		db.session.add(cash)
		db.session.commit()
		#cashes=Cash.query.all()
		#return render_template('liststudentspayments.html',payments=payments, customer=customer)
		return redirect(url_for('add_payment',customer_id=customer_id)) 	
	else:
		#cashes=Cash.query.all()
		flash=("Sono entrato in ADD_CASH con GET... ekkekkazzo, no!!!!")
		return render_template('newcash.html',customer=customer, payment_quote=payment_quote)

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

@app.route('/listpayments')
def list_payments():
	payments=Payment.query.all()
	return render_template('listpayments.html', payments=payments)

@app.route('/listreceipts')
def list_receipts():
	receipts=Receipt.query.all()
	return render_template('listreceipts.html', receipts=receipts)

@app.route('/listusers')
def list_users():
	users=User.query.all()
	return render_template('listusers.html', users=users)

@app.route('/search', methods=['GET','POST'])
def search():
	return render_template('search.html')

@app.route('/listcashes', methods=['GET','POST'])
def list_cashes():
	cashes=Cash.query.all()
	return render_template('listcashes.html', cashes=cashes)

@app.route('/casheet/<user_id>', methods=['GET','POST'])
def cash_sheet(user_id):
	tot=0
	usercashes=Cash.query.filter_by(user_id=user_id, vault=0).all()
	tot = Cash.query(func.sum(Cash.cash001)).filter_by(user_id=user_id).first()
	return render_template('casheet.html', user=session.get('user'),usercashes=usercashes, day=date.today(), tot=tot)