"""RoomMatch"""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Listing, UserListing, Friendship, Picture, Question, Answer, UserAnswer
from model import connect_to_db, db 
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = "Super Secret"
app.jinja_env.undefined = StrictUndefined

STATES = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN",
"KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", 
"NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]

@app.route("/")
def index():
	"""Homepage"""
	return render_template("homepage.html")


@app.route("/register")
def registration_page():
	"""Page to input info and friends"""

	users = User.query.all()

	return render_template("registration.html", users=users, STATES=STATES)


@app.route("/make_user_profile", methods=["POST"])
def make_profile(): 
	"""add user info to database"""

	user_name = request.form.get("user_name")
	name = request.form.get("full_name")
	email = request.form.get("email")
	password = request.form.get("password")
	phone = request.form.get("phone")
	bio = request.form.get("bio")
	photo = request.form.get("photo")
	state = request.form.get("state")
	looking_for_apt = request.form.get("looking")
	friends = request.form.getlist("friends")

	result = db.session.query(func.max(User.user_id)).one()
   	max_id = int(result[0])
   	user_id = max_id + 1

	db.session.add(User(user_name=user_name,
                        name=name,
                        email=email, 
                        password=password, 
                        phone=phone, 
                        bio=bio, 
                        state=state, 
                        photo=photo, 
                        looking_for_apt=looking_for_apt, 
                        ))


	for friend in friends: 
		db.session.add(Friendship(friend_1_id=friend, 
								friend_2_id=user_id))
		db.session.add(Friendship(friend_2_id=friend, 
								friend_1_id=user_id))

	db.session.commit()

	session["current_user"] = user_id

	return redirect("/")
		


@app.route("/users/<int:user_id>")
def user_profile(user_id):
	"""query for user info to display"""

	user = User.query.get(user_id)

	return render_template("user_profile.html", user=user)

@app.route("/listings/<int:listing_id>")
def listing_profile(listing_id):
	"""query for listing info to display"""

	listing = Listing.query.get(listing_id)

	return render_template("listing_profile.html", listing=listing)


@app.route('/add_listing', methods=["POST"])
def add_listing():
    """add listing to database"""

    neighborhood = request.form.get("neighborhood")
    address = request.form.get("address")
    price = request.form.get("price")
    avail_as_of = request.form.get("avail_as_of")
    length_of_rental = request.form.get("length")
    bedrooms = request.form.get("bedrooms")
    bathrooms = request.form.get("bathrooms")
    laundry = request.form.get("laundry")
    pets = request.form.get("pets")
    description = request.form.get("description")

    user_id = session["current_user"]
    result = db.session.query(func.max(Listing.listing_id)).one()
    max_id = int(result[0])
    listing_id = max_id + 1

    db.session.add(Listing(neighborhood=neighborhood,
                        address=address,
                        price=price, 
                        avail_as_of=avail_as_of, 
                        length_of_rental=length_of_rental, 
                        bedrooms=bedrooms, 
                        bathrooms=bathrooms, 
                        laundry=laundry, 
                        pets=pets, 
                        description=description
                        ))

    db.session.add(UserListing(user_id=user_id,
    					listing_id=listing_id
                        ))

    db.session.commit()


    return redirect("/listings/{}".format(listing_id))



@app.route("/house_search")
def find_houses():
	"""query for houses that fit the description"""

	live_alone = request.args.get("live_alone")
	duration = request.args.get("duration")
	price_cap = request.args.get("price_cap")
	start_date = request.args.get("start_date")
	neighborhood = request.args.get("neighborhood")


@app.route("/login", methods=['POST'])
def login():
    """Log In user."""

    user_info = db.session.query(User.email, User.password).all()

    email = request.form.get("email")
    password = request.form.get("password")
    user = (email, password)

    try: 
    	user_id = db.session.query(User.user_id).filter(User.email == email).one()[0]
    	if user in user_info:
        	session['current_user'] = user_id
        	flash('Successfully logged in as {}'.format(email))
        	return redirect("/users/{}".format(user_id))
    	else:
        	flash("Ya gotta sign up first!")
    except: 
    	flash("Ya gotta sign up first!")
    	return redirect("/")


@app.route("/logout")
def logout():
    """Log Out user."""

    del session['current_user']
    flash('Successfully logged out')

    return redirect("/")






if __name__ == "__main__":

	app.debug = True
	app.jinja_env.auto_reload = app.debug

	connect_to_db(app)

	DebugToolbarExtension(app)

	app.run(port=5000, host='0.0.0.0')


