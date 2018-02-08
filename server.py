"""RoomMatch"""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Listing, UserListing, Friendship, Picture, Question, Answer, UserAnswer
from model import connect_to_db, db 
from sqlalchemy import func
import functions

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

    kwargs = dict(
    user_id = request.form.get("user_name"),
    name = request.form.get("full_name"),
    email = request.form.get("email"),
    password = request.form.get("password"),
    phone = request.form.get("phone"),
    bio = request.form.get("bio"),
    photo = request.form.get("photo"),
    state = request.form.get("state"),
    looking_for_apt = request.form.get("looking"),
    friends = request.form.getlist("friends"))
    
    if User.query.get(kwargs[user_id]):
        flash("User Name Taken")
        return redirect("/users/{}".format(kwargs[user_id]))
    else: 
        for key in kwargs.keys(): 
            if kwargs[key] == "":
                del kwargs[key]
        db.session.add(User(**kwargs))
        db.session.commit()

        for friend in kwargs[friends]: 
            db.session.add(Friendship(friend_1_id=friend, 
                                    friend_2_id=user_id))
            # db.session.flush()
            db.session.add(Friendship(friend_2_id=friend, 
                                    friend_1_id=user_id))

        db.session.commit()

        session["current_user"] = kwargs[user_id]

        return redirect("/")
            


@app.route("/users/<user_id>")
def user_profile(user_id):
    """query for user info to display"""

    user = User.query.get(user_id)
    photos = {}
    listings = user.listings
    for listing in listings: 
        if listing.photos: 
            photos[listing.listing_id] = listing.photos[0].photo

    return render_template("user_profile.html", user=user, photos=photos)

@app.route("/listings/<listing_id>")
def listing_profile(listing_id):
    """query for listing info to display"""

    users = User.query.all()
    listing = Listing.query.get(listing_id)
    lister = False
    friends = []
    mutuals = []
    if session.get("current_user"):
        user = User.query.get(session["current_user"])
        print session["current_user"]
        if user in listing.users: 
            lister = True
        else: 
            friends = functions.friends_in_listing(user, listing)
            mutuals = functions.mutual_friends_in_listing(user, listing)

    return render_template("listing_profile.html", listing=listing, users=users, lister=lister, friends=friends, mutuals=mutuals)


@app.route('/add_listing', methods=["POST"])
def add_listing():
    """add listing to database"""

    kwargs = dict(listing_id = request.form.get("listing_name"),
    neighborhood = request.form.get("neighborhood"),
    address = request.form.get("address"),
    price = request.form.get("price"),
    avail_as_of = request.form.get("avail_as_of"),
    length_of_rental = request.form.get("length"),
    bedrooms = request.form.get("bedrooms"),
    bathrooms = request.form.get("bathrooms"),
    laundry = request.form.get("laundry"),
    pets = request.form.get("pets"),
    description = request.form.get("description"),
    main_photo = request.form.get("main_photo"),
    active = request.form.get("active"))

    user_id = session["current_user"]

    if Listing.query.get(kwargs[listing_id]):
        flash("Listing Name Taken")
        return redirect("/listings/{}".format(kwargs[listing_id]))
    else: 
        db.session.add(Listing(**kwargs))
        db.session.commit()
        db.session.add(UserListing(user_id=user_id,
                            listing_id=listing_id
                            ))

        db.session.commit()

        return redirect("/listings/{}".format(listing_id))

@app.route("/add_roommate", methods=["POST"])
def add_roommate(): 
    """add a roommate to current listing"""

    listing_id = request.form.get("listing_id")
    user_id = request.form.get("roomie")
    print "test"
    print listing_id
    print user_id
    db.session.add(UserListing(user_id=user_id,
                            listing_id=listing_id
                            ))

    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/add_self_as_roommate", methods=["POST"])
def add_self_as_roommate(): 
    """add yourself as a roommate to current listing"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    db.session.add(UserListing(user_id=user_id,
                            listing_id=listing_id
                            ))

    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/listings_by_state")
def listings_by_state():
    """display all listings sorted by state"""

    listings_by_state = {}

    for state in STATES: 
        listings = Listing.query.filter(Listing.address.like('%{}%'.format(state))).all()
        listings_by_state[state] = listings
    
    return render_template("/listings_by_state.html", STATES=STATES, listings_by_state=listings_by_state)


@app.route("/users_by_state")
def users_by_state():
    """display all users sorted by state"""

    users_by_state = {}

    for state in STATES: 
        users = User.query.filter_by(state=state).all()
        users_by_state[state] = users
    
    return render_template("/users_by_state.html", STATES=STATES, users_by_state=users_by_state)


@app.route("/listings_by_friends")
def listings_by_friends():
    """display all listings by your friends"""

    if "current_user" in session: 
        user = User.query.get(session["current_user"])
        friends = functions.get_all_friends(user)
        seconds = functions.get_all_second_degree_friends(user)

        return render_template("/listings_by_friends.html",  friends=friends, seconds=seconds)
    else: 
        flash("Don't forget to log in!")
        return redirect("/")

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


