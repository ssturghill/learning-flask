from flask import Flask, render_template, request, make_response, jsonify, session, redirect, url_for
from models import db, User
from forms import SignupForm, LoginForm, AddressForm
from flask_cors import CORS, cross_origin
import aiml
import os
import xml.etree.ElementTree as ET
from flask_responses import json_response, xml_response, auto_response
from flask_login import login_manager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:BeoWulf16@localhost/learningflask'
db.init_app(app)

app.secret_key = "development-key"

cors = CORS(app, resources={r"^": {"origins": "*"}})
app.debug = True

def csrf_json_header_add():
    headers = {}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = '*'
    headers['Access-Control-Allow-Domain'] = '*'
    headers['Access-Control-Allow-Credentials'] = True
    return headers

def csrf_header_add(resp):
    resp.status_code = 201
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = '*'
    resp.headers['Access-Control-Allow-Domain'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = True
    resp.status_code = 201
    return resp

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/gallery")
def gallery():
  return render_template("gallery.html")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if 'email' in session:
        return redirect(url_for('home'))
    form = SignupForm()

    if request.method == "POST":
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()

            session['email'] = newuser.email
            return redirect(url_for('home'))

    elif request.method == "GET":
        return render_template('signup.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'email' in session:
        return redirect(url_for('home'))

    form = LoginForm()

    if request.method == "POST":
        if form.validate() == False:
            return render_template("login.html", form=form)
        else:
            email = form.email.data
            password = form.password.data

            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                session['email'] = form.email.data
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))

    elif request.method == 'GET':
        return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    chat = request.args.get('chat').rstrip()
    kernel = aiml.Kernel()

    if os.path.isfile("aiml/bot_brain.brn"):
        kernel.bootstrap(brainFile="aiml/bot_brain.brn")
    else:
        kernel.bootstrap(learnFiles="aiml/basic_chat.xml")
        kernel.saveBrain("aiml/bot_brain.brn")

    resp = make_response(kernel.respond(chat))
    resp = csrf_header_add(resp)
    return resp

@app.route("/home")
def home():
    if 'email' not in session:
        return redirect(url_for('login'))

    return render_template("home.html")


if __name__ == "__main__":
  app.run(debug=True)
