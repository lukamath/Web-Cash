from flask import Flask, request, render_template, url_for, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

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
	receipt_id=db.Column(db.Integer, db.ForeignKey('receipt.id'))
	receipt=db.relationship('Receipt',backref='payment')

class Customer(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(25), nullable=False)
	surname=db.Column(db.String(25), nullable=False)
	tax_code=db.Column(db.String(16), nullable=False)
	receipts=db.relationship('Receipt',backref='customer', lazy=True)

@app.route('/')
def index():
	return render_template('index.html')