"""RoomMatch"""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Listing, UserListing, Friendship, Picture, Question, Answer, UserAnswer
from model import connect_to_db, db 
from sqlalchemy import func
import functions
import datetime

app = Flask(__name__)
app.secret_key = "Super Secret"
app.jinja_env.undefined = StrictUndefined

STATES = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN",
"KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", 
"NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]

UPLOAD_FOLDER = "static/uploaded_images/"

@app.route("/")
def index():
    """Homepage"""
    neighborhoods = db.session.query(Listing.neighborhood).group_by(Listing.neighborhood).all()
    neighborhoods = [neighborhood[0] for neighborhood in neighborhoods]

    return render_template("homepage.html", neighborhoods=neighborhoods)

@app.route("/test_react")
def test_react(): 
    """test react"""
    return render_template("/react.html")

@app.route("/test_maps")
def test_maps(): 
    """test maps"""

    address = "1600+Amphitheatre+Parkway,+Mountain+View,+CA"
    geocode = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyALsH-wBDg1jGymSzRN4cIL8rTVQo87PwM".format(address)
    print geocode

    return render_template("/maps.html", address=address, geocode=geocode)



@app.route("/register")
def registration_page():
    """Page to input info and friends"""

    users = User.query.all()
    listings = Listing.query.all()
    questions = Question.query.all()
    
    return render_template("registration.html", users=users, STATES=STATES, listings=listings, questions=questions)


@app.route("/add_listing")
def listing_page():
    """Page to input info about a home"""

    users = User.query.all()

    return render_template("create_listing.html", users=users, STATES=STATES)


@app.route("/make_user_profile", methods=["POST"])
def make_profile(): 
    """add user info to database"""

    friends = request.form.getlist("friends")
    listings = request.form.getlist("listings")
    looking = True if request.form.get("looking") == "True" else False
    questions = Question.query.all()
    user_id = request.form.get("user_name")
    

    photo = functions.save_photo("photo")

    kwargs = dict(
    user_id=user_id,
    name=request.form.get("full_name"),
    email=request.form.get("email"),
    password=request.form.get("password"),
    phone=request.form.get("phone"),
    bio=request.form.get("bio"),
    photo=photo,
    state=request.form.get("state"),
    looking_for_apt=looking,
    )
    
    if User.query.get(user_id):
        flash("User Name Taken")
        return redirect("/users/{}".format(user_id))
    else: 
        for key in kwargs.keys(): 
            if kwargs[key] == "":
                del kwargs[key]
        db.session.add(User(**kwargs))
        db.session.commit()

        for friend in friends: 
            db.session.add(Friendship(friend_1_id=friend, 
                                    friend_2_id=user_id))
            # db.session.flush()
            db.session.add(Friendship(friend_2_id=friend, 
                                    friend_1_id=user_id))

        db.session.commit()

        for listing in listings: 
            functions.add_UserListing(user_id, listing)


        for question in questions: 
            answer_id = request.form.get("{}".format(question.question_id))

            db.session.add(UserAnswer(user_id=user_id, 
                                    answer_id=answer_id))

        db.session.commit()

        session["current_user"] = user_id

        return redirect("/users/{}".format(user_id))
            

@app.route("/make_listing_profile", methods=["POST"])
def make_listing_profile(): 
    """add listing info to database"""


    roommates = request.form.getlist("roommates")
    print roommates

    laundry = True if request.form.get("laundry") == "True" else False
    pets = True if request.form.get("pets") == "True" else False
    listing_id = request.form.get("listing_name")

    main_photo = functions.save_photo("main_photo")

    photos = []
    photos.append(functions.save_photo("photo_1"))
    photos.append(functions.save_photo("photo_2"))
    photos.append(functions.save_photo("photo_3"))


    kwargs = dict(
        listing_id=listing_id,
        address=request.form.get("address"),
        neighborhood=request.form.get("neighborhood"),
        price=int(request.form.get("price")),
        avail_as_of=request.form.get("avail_date"),
        length_of_rental=request.form.get("duration"),
        main_photo=main_photo,
        bedrooms=request.form.get("bedrooms"),
        bathrooms=request.form.get("bathrooms"),
        laundry=laundry,
        pets=pets,
        description=request.form.get("description")
    )
    
    if Listing.query.get(listing_id):
        flash("Listing Name Taken")
        return redirect("/listings/{}".format(listing_id))
    else: 
        for key in kwargs.keys(): 
            if kwargs[key] == "":
                del kwargs[key]
        db.session.add(Listing(**kwargs))
        db.session.commit()

        db.session.add(UserListing(user_id=session["current_user"], 
                                    listing_id=listing_id, 
                                    primary_lister=True))

        db.session.commit()

        for roommmate in roommates: 
            functions.add_UserListing(roommate, listing_id)

        db.session.commit()

        for photo in photos: 
            db.session.add(Picture(listing_id=listing_id, 
                                   photo=photo))
        db.session.commit()

        return redirect("/listings/{}".format(listing_id))



@app.route("/users/<user_id>")
def user_profile(user_id):
    """query for user info to display"""

    user = User.query.get(user_id)
    try: 
        me = User.query.get(session["current_user"])
        listings = user.listings
        answers = functions.get_common_answers(me, user)
        # favorites = user.favorites()

        return render_template("user_profile.html", user=user, answers=answers)
    except: 
        flash("Don't forget to log in!")
        return redirect("/")


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


@app.route("/add_favorite", methods=["POST"])
def add_favorite(): 
    """add listing as favorite"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    db.session.add(UserListing(user_id=session["current_user"], 
                                    listing_id=listing_id, 
                                    favorite=True))

    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/remove_favorite", methods=["POST"])
def remove_favorite(): 
    """remove listing as favorite"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    UserListing.query.filter_by(user_id=user_id, listing_id=listing_id, favorite=True).delete()

    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/deactivate_listing", methods=["POST"])
def deactivate(): 
    """take listing off market"""

    listing_id = request.form.get("listing_id")
    listing = Listing.query.get(listing_id)
    listing.active = False
    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/reactivate_listing", methods=["POST"])
def reactivate(): 
    """put listing on market with new dates"""

    listing_id = request.form.get("listing_id")
    avail_as_of = request.form.get("avail")
    listing = Listing.query.get(listing_id)
    listing.active = True
    listing.avail_as_of = avail_as_of
    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/add_roommate", methods=["POST"])
def add_roommate(): 
    """add a roommate to current listing"""

    listing_id = request.form.get("listing_id")
    user_id = request.form.get("roomie")

    functions.add_UserListing(user_id, listing_id)

    return redirect("/listings/{}".format(listing_id))


@app.route("/add_self_as_roommate", methods=["POST"])
def add_self_as_roommate(): 
    """add yourself as a roommate to current listing"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    functions.add_UserListing(user_id, listing_id)

    return redirect("/listings/{}".format(listing_id))


@app.route("/remove_roommate", methods=["POST"])
def remove_roommate(): 
    """remove a roommate from current listing"""

    listing_id = request.form.get("listing_id")
    user_id = request.form.get("roomie")
    
    functions.delete_UserListing(user_id, listing_id)

    return redirect("/listings/{}".format(listing_id))


@app.route("/remove_self_as_roommate", methods=["POST"])
def remove_self_as_roommate(): 
    """delete yourself as a roommate from current listing"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    functions.delete_UserListing(user_id, listing_id)

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
        users = User.query.filter(User.state == state).all()
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


@app.route("/listings_by_friends_in_state")
def listings_by_friends_in_state():
    """display all listings by your friends in your state, sorted by neighborhood"""

    if "current_user" in session: 
        user = User.query.get(session["current_user"])
        listings = functions.get_all_listings_by_friends_of_any_degree(user)
        state = user.state
        neighborhoods = set()
        for listing in listings: 
            if state in listing.address: 
                neighborhoods.add(listing.neighborhood)

        return render_template("/listings_by_friends_in_state.html",  state=state, listings=listings, neighborhoods=neighborhoods)
    else: 
        flash("Don't forget to log in!")
        return redirect("/")


@app.route("/house_search")
def find_houses():
    """query for houses that fit the description"""

    live_alone = request.args.get("live_alone")
    duration = request.args.get("duration")
    price_cap = int(request.args.get("price_cap"))
    start_date = request.args.get("start_date")
    neighborhood = request.args.get("neighborhood")
    user = User.query.get(session["current_user"])
    listings_by_friends = functions.get_all_listings_by_friends_of_any_degree(user)

    listings = []
    right_location = Listing.query.filter(Listing.neighborhood == neighborhood).all()
    for listing in right_location: 
        print start_date
        print str(listing.avail_as_of)
       
        if listing.price <= price_cap and str(listing.avail_as_of) >= start_date: 
            listings.append(listing)
  
    return render_template("/house_search_results.html", listings=listings, listings_by_friends=listings_by_friends)


@app.route("/roommate_search")
def find_roommates():
    """query for roommates in state"""

    user = session["current_user"]
    state = User.query.get(user).state
    users = User.query.all()
    users_in_state = []
    for user in users: 
        if user.state == state:
            users_in_state.append(user)
    return render_template("/roommate_search_results.html")


@app.route("/mutuals")
def mutuals(user): 
    """takes a user_name and returns a list of mutual friends with current user"""

    return functions.mutual_friends(session["current_user"], user)
    

@app.route("/login", methods=['POST'])
def login():
    """Log In user."""

    user_info = db.session.query(User.email, User.password).all()

    email = request.form.get("email")
    password = request.form.get("password")
    user = (email, password)

    name = request.form.get("name")
    user_id = request.form.get("id")
    print " test" 
    print name
    print user_id
    
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


@app.route("/listing-info.json")
def listing_info(): 
    """returns listing info as JSON"""

    listing_id = request.args.get("listing_id")
    listing = Listing.query.get(listing_id)
    user = User.query.get(session["current_user"])
    friends = functions.mutual_friends_in_listing(user, listing)
    friends = [(friend.name, friend.photo) for friend in friends]

    info = {
        "price" : listing.price, 
        "start date": listing.avail_as_of, 
        "friends" : friends}

    return jsonify(info)


if __name__ == "__main__":

    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')


