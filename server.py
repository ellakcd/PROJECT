"""RoomMatch"""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Listing, Req, Friendship, Picture, Question, Answer, User_answer
from model import connect_to_db, db 

app = Flask(__name__)
app.secret_key = "Super Secret"
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
	"""Homepage"""
	return render_template("homepage.html")












if __name__ = "__main__":

	app.debug = True
	app.jinja.env.auto_reload = app.debug

	connect_to_db(app)

	DebugToolbarExtension(app)

	app.run(port=5000, host='0.0.0.0')


