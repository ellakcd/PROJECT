"""RoomMatch"""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Listing, UserListing, Friendship, Picture, Question, Answer, UserAnswer
from model import connect_to_db, db 

app = Flask(__name__)
app.secret_key = "Super Secret"
app.jinja_env.undefined = StrictUndefined

@app.route("/")
def index():
	"""Homepage"""
	return render_template("homepage.html")


@app.route("/register")
def registration_page():
	return render_template("registration.html")


@app.route("/users/<int:user_id>")
def user_profile():
	"""query for user info to display"""

	user = User.query.get(user_id)

	return render_template("user_profile.html", user=user)



@app.route("/house_search")
def find_houses():
	"""query for houses that fit the description"""

	live_alone = request.args.get("live_alone")
	duration = request.args.get("duration")
	price_cap = request.args.get("price_cap")
	start_date = request.args.get("start_date")
	neighborhood = request.args.get("neighborhood")





if __name__ == "__main__":

	app.debug = True
	app.jinja.env.auto_reload = app.debug

	connect_to_db(app)

	DebugToolbarExtension(app)

	app.run(port=5000, host='0.0.0.0')


