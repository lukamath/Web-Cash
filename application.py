from flask import Flask, request, render_template, url_for, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

app=Flask(__name__)

app.config['SECRET_KEY']='uOzPG137aJNoq2bBJ4b9P81DY5vCiRXj'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db_billing.db'
db=SQLAlchemy(app)	



