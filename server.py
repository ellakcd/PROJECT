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

    neighborhoods = set()
    state = ""
    if "current_user" in session: 
        state = User.query.get(session["current_user"]).state

    if state: 
        listings = Listing.query.filter(Listing.address.like('%{}%'.format(state))).all()
        for listing in listings: 
            neighborhoods.add(listing.neighborhood)


    return render_template("homepage.html", neighborhoods=neighborhoods, STATES=STATES, state=state)


# @app.route("/test_react")
# def test_react(): 
#     """test react"""
#     return render_template("/react.html")



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

    laundry = True if request.form.get("laundry") == "True" else False
    pets = True if request.form.get("pets") == "True" else False
    living_there = True if request.form.get("living_there") == "True" else False
    listing_id = request.form.get("listing_name")
    user_id = session["current_user"]

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
        description=request.form.get("description"), 
        primary_lister = user_id
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

        if living_there: 
            functions.add_UserListing(user_id, listing_id)

        for roommate in roommates: 
            functions.add_UserListing(roommate, listing_id)

        for photo in photos: 
            db.session.add(Picture(listing_id=listing_id, 
                                   photo=photo))
        db.session.commit()

        return redirect("/listings/{}".format(listing_id))



@app.route("/users/<user_id>")
def user_profile(user_id):
    """query for user info to display"""

    user = User.query.get(user_id)
    listings = user.listings
    answers = []
    favorites = []
    my_page = False
    are_friends = False
    if session.get("current_user"):
        me = User.query.get(session["current_user"])
        are_friends = functions.are_friends(me, user)
        answers = functions.get_common_answers(me, user)
        favorites = me.favorites
        favorites = [favorite for favorite in favorites if favorite.active]
        mutuals = functions.mutual_friends(me, user)
        if me.user_id == user.user_id: 
            my_page = True

    return render_template("user_profile.html", user=user, answers=answers, my_page=my_page, are_friends=are_friends, mutuals=mutuals)



@app.route("/listings/<listing_id>")
def listing_profile(listing_id):
    """query for listing info to display"""

    users = User.query.all()
    listing = Listing.query.get(listing_id)
    lister = False
    favorite = False
    friends = []
    mutuals = []
    if session.get("current_user"):
        user = User.query.get(session["current_user"])
        if listing in user.favorites:
            favorite = True
        if user in listing.users: 
            lister = True
        else: 
            friends = functions.friends_in_listing(user, listing)
            mutuals = functions.mutual_friends_in_listing(user, listing)

    return render_template("listing_profile.html", listing=listing, users=users, lister=lister, friends=friends, mutuals=mutuals, favorite=favorite)


@app.route("/add_as_friend", methods=["POST"])
def add_as_friend(): 
    """add as user as a friend"""

    user_id = request.form.get("user_id")
    me = session["current_user"]

    functions.add_friendship(user_id, me)

    return redirect("/users/{}".format(user_id))



@app.route("/add_favorite", methods=["POST"])
def add_favorite(): 
    """add listing as favorite"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    functions.add_favorite(user_id, listing_id)

    return redirect("/listings/{}".format(listing_id))


@app.route("/remove_favorite", methods=["POST"])
def remove_favorite(): 
    """remove listing as favorite"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    functions.delete_favorite(user_id, listing_id)

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

@app.route("/change_primary", methods=["POST"])
def change_primary(): 
    """change primary lister"""

    listing_id = request.form.get("listing_id")
    user_id = request.form.get("new_primary")
    listing = Listing.query.get(listing_id)
    listing.primary_lister = user_id
    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/deactivate_user", methods=["POST"])
def deactivate_user(): 
    """take user off market"""

    user = functions.get_current_user()
    user.looking_for_apt = False
    db.session.commit()

    return redirect("/users/{}".format(session["current_user"]))


@app.route("/reactivate_user", methods=["POST"])
def reactivate_user(): 
    """put user back in play"""

    user = functions.get_current_user()
    user.looking_for_apt = True
    db.session.commit()

    return redirect("/users/{}".format(session["current_user"]))


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



@app.route("/listings_by_friends_in_state")
def listings_by_friends_in_state():
    """display all listings by your friends in your state, sorted by neighborhood"""

    # if "current_user" in session: 
    #     user = User.query.get(session["current_user"])
    user = functions.get_current_user()
    listings = functions.get_all_listings_by_friends_of_any_degree(user)
    listings = [listing for listing in listings if listing not in user.listings]
    listings = [listing for listing in listings if listing.active]
    state = user.state
    neighborhoods = set()
    for listing in listings: 
        if state in listing.address: 
            neighborhoods.add(listing.neighborhood)

    return render_template("/listings_by_friends_in_state.html",  state=state, listings=listings, neighborhoods=neighborhoods)
    # else: 
    #     flash("Don't forget to log in!")
    #     return redirect("/")


@app.route("/listings_by_friends_in_state.json")
def listing_friend_state_json():
    """send listings by friends in state as json"""

    user = functions.get_current_user()
    state = user.state
    listings = functions.get_all_listings_by_friends_of_any_degree(user)
    listings = [listing for listing in listings if listing not in user.listings]
    listings = [listing for listing in listings if listing.active]
    listings = [listing for listing in listings if state in listing.address] 

    addresses = []
    for listing in listings:
        addresses.append((listing.address, listing.listing_id))

    info = {"addresses" : addresses}

    return jsonify(info)


@app.route("/user_friends_in_state")
def user_friends_in_state():
    """display all users friends with your friends in your state"""

    # if "current_user" in session: 
    #     user = User.query.get(session["current_user"])
    user = functions.get_current_user()
    friends = functions.get_all_friends_of_any_degree(user)

    state = user.state

    users = [friend for friend in friends if friend.state == state]
    users = [user for user in users if user.looking_for_apt]

    return render_template("/users_w_friends_in_state.html", state=state, users=users)
    # else: 
    #     flash("Don't forget to log in!")
    #     return redirect("/")



@app.route("/update_state", methods=["POST"])
def update_state():
    """update user's state"""

    state = request.form.get("state")
    user = functions.get_current_user()
    user.state = state
    db.session.commit()

    return redirect("/")


@app.route("/house_search")
def find_houses():
    """query for houses that fit the description"""

    live_alone = request.args.get("live_alone")
    duration = request.args.get("duration")
    price_cap = int(request.args.get("price_cap"))
    start_date = request.args.get("start_date")
    neighborhoods = request.args.getlist("neighborhoods")
    user = functions.get_current_user()
    listings_by_friends = functions.get_all_listings_by_friends_of_any_degree(user)
    state = user.state

    listings = functions.get_listings(state, neighborhoods, price_cap, live_alone, start_date)
    
  
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


# @app.route("/mutuals")
# def mutuals(user): 
#     """takes a user_name and returns a list of mutual friends with current user"""

#     return functions.mutual_friends(session["current_user"], user)
    

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


@app.route("/user-info.json")
def user_info(): 
    """returns user info as JSON"""

    user_id = request.args.get("user_id")
    user2 = User.query.get(user_id)
    user = User.query.get(session["current_user"])
    friends = functions.mutual_friends(user, user2)
    friends = [(friend.name, friend.photo) for friend in friends]
    answers = functions.get_common_answers(user, user2)

    info = {
        "answers" : answers, 
        "friends" : friends}

    return jsonify(info)


if __name__ == "__main__":

    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')


