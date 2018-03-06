"""RoomMatch"""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Listing, UserListing, Friendship, Picture, Question, Answer, UserAnswer, Message
from model import connect_to_db, db 
from sqlalchemy import func
import functions
import datetime
import bcrypt

app = Flask(__name__)
app.secret_key = "Super Secret"
app.jinja_env.undefined = StrictUndefined

STATES = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN",
"KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", 
"NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]

MONTHS = [(1, "Jan"), (2, "Feb"), (3, "March"), (4, "April"), (5, "May"), (6, "June"), (7, "July"), (8, "Aug"), (9, "Sept"), (10, "Oct"), (11, "Nov"), (12, "Dec")]

UPLOAD_FOLDER = "static/uploaded_images/"


# LANDING PAGES
@app.route("/")
def index():
    """Homepage"""

    user = None
    users = User.query.all()
    listings = Listing.query.all()
    questions = Question.query.all()
    state = ""
    if "current_user" in session: 
        user = User.query.get(session["current_user"])
        state = user.state

    neighborhoods = functions.get_neighborhoods(state)
    filters = ["price_cap", "laundry", "friends", "pets", "roommates", "neighborhoods", "start_dates", "duration"]

    return render_template("homepage.html", neighborhoods=neighborhoods, users=users, user=user, listings=listings, questions=questions, filters=filters, STATES=STATES, months=MONTHS, state=state)


# @app.route("/register")
# def registration_page():
#     """Page to input info and friends"""

#     users = User.query.all()
#     listings = Listing.query.all()
#     questions = Question.query.all()
#     user = None
    
#     return render_template("registration.html", users=users, STATES=STATES, user=user, listings=listings, questions=questions)


# @app.route("/add_listing")
# def listing_page():
#     """Page to input info about a home"""

#     users = User.query.all()
#     user = User.query.get(session["current_user"])

#     return render_template("create_listing.html", users=users, user=user, STATES=STATES)


@app.route("/users/<user_id>")
def user_profile(user_id):
    """query for user info to display"""

    user = User.query.get(user_id)
    common_answers = []
    favorites = []
    mutuals = []
    message_dict = {}
    my_page = False
    are_friends = False
    me = None
    properties = Listing.query.filter(Listing.primary_lister == user_id)
    properties = [prop for prop in properties if prop not in user.listings]
    if session.get("current_user"):
        me = User.query.get(session["current_user"])
        are_friends = functions.are_friends(me, user)
        common_answers = functions.get_common_answers(me, user)
        favorites = me.favorites
        favorites = [favorite for favorite in favorites if favorite.active]
        mutuals = functions.mutual_friends(me, user)
        if me.user_id == user.user_id: 
            all_users = User.query.all()
            all_users = [user_not_me for user_not_me in all_users if user_not_me != me]
            message_dict = me.get_messages()
            all_users = [user_not_partner for user_not_partner in all_users if user_not_partner.user_id not in message_dict]
            print message_dict
            print all_users
            return render_template("my_profile.html", page_user=me, user=me, all_users=all_users, properties=properties, message_dict=message_dict, STATES=STATES)


    return render_template("user_profile.html", page_user=user, user=me, properties=properties, common_answers=common_answers, my_page=my_page, are_friends=are_friends, mutuals=mutuals, message_dict=message_dict)



@app.route("/listings/<listing_id>")
def listing_profile(listing_id):
    """query for listing info to display"""

    users = User.query.all()
    me = None
    listing = Listing.query.get(listing_id)
    primary_lister = {}
    lister = False
    am_primary = False
    favorite = False
    friends = []
    mutuals = []
    avail_date = "{}/{}/{}".format(listing.avail_as_of.month, listing.avail_as_of.day, listing.avail_as_of.year)
    primary = User.query.get(listing.primary_lister)
    if primary not in listing.users:
        photo = primary.photo
        primary_lister = {"id": primary.user_id, 
                        "photo": photo}

    if session.get("current_user"):
        me = User.query.get(session["current_user"])
        if listing in me.favorites:
            favorite = True
        if me in listing.users: 
            lister = True
        if me.user_id == listing.primary_lister:
            am_primary = True
        else: 
            friends = functions.friends_in_listing(me, listing)
            mutuals = functions.mutual_friends_in_listing(me, listing)

    return render_template("listing_profile.html", listing=listing, user=me, avail_date=avail_date, users=users, lister=lister, am_primary=am_primary, primary_lister=primary_lister, friends=friends, mutuals=mutuals, favorite=favorite)


@app.route("/listings_by_state")
def listings_by_state():
    """display all listings sorted by state"""

    listings_by_state = {}

    user = None

    for state in STATES: 
        listings = Listing.query.filter(Listing.address.like('%{}%'.format(state))).all()
        listings = [listing for listing in listings if listing.active]
        if listings: 
            listings_by_state[state] = listings
    
    return render_template("/listings_by_state.html", STATES=STATES, user=user, listings_by_state=listings_by_state)


@app.route("/users_by_state")
def users_by_state():
    """display all users sorted by state"""

    users_by_state = {}

    user = None

    for state in STATES: 
        users = User.query.filter(User.state == state).all()
        users = [user for user in users if user.looking_for_apt]
        if users: 
            users_by_state[state] = users
    
    return render_template("/users_by_state.html", STATES=STATES, user=user, users_by_state=users_by_state)



@app.route("/listings_by_friends_in_state")
def listings_by_friends_in_state():
    """display all listings by your friends in your state, sorted by neighborhood"""

    if "current_user" in session: 
        user = User.query.get(session["current_user"])
        state = user.state
        listings = functions.get_all_listings_by_friends_of_any_degree(user)
        listings = [listing for listing in listings if listing.active]
        listings = [listing for listing in listings if not functions.user_in_listing(listing)]
        listings = [listing for listing in listings if state in listing.address]
        
        neighborhoods = set()
        for listing in listings: 
            neighborhoods.add(listing.neighborhood)

        listing_names = [listing.listing_id for listing in listings]
        listing_names = "|".join(listing_names)
        print listing_names

        return render_template("/listings_by_friends_in_state.html",  user=user, state=state, listings=listings, neighborhoods=neighborhoods, listing_names=listing_names)
    else: 
        flash("Don't forget to log in!")
        return redirect("/")


@app.route("/user_friends_in_state")
def user_friends_in_state():
    """display all users friends with your friends in your state"""

    if "current_user" in session: 
        user = User.query.get(session["current_user"])
        friends = functions.get_all_friends_of_any_degree(user)

        state = user.state

        users = [friend for friend in friends if friend.state == state]
        users = [user for user in users if user.looking_for_apt]

        return render_template("/users_w_friends_in_state.html", user=user, state=state, users=users)
    else: 
        flash("Don't forget to log in!")
        return redirect("/")


# REDIRECTS
@app.route("/make_user_profile", methods=["POST"])
def make_profile(): 
    """add user info to database"""

    friends = request.form.getlist("friends")
    listings = request.form.getlist("listings")
    looking = True if request.form.get("looking") == "True" else False
    questions = Question.query.all()
    user_id = request.form.get("user_name")
    password = request.form.get("password").encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print hashed
    # hashed = password
    venmo = request.form.get("venmo")

    photo = functions.save_photo("photo")

    kwargs = dict(
    user_id=user_id,
    name=request.form.get("full_name"),
    email=request.form.get("email"),
    password=hashed,
    phone=request.form.get("phone"),
    bio=request.form.get("bio"),
    photo=photo,
    state=request.form.get("state"),
    looking_for_apt=looking,
    venmo=venmo
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


@app.route("/add_message", methods=["POST"])
def create_message():
    """add a message between two users"""

    receiver_id = request.form.get("user_id")
    me = session["current_user"]
    content = request.form.get("message")
    print "receiver"
    print receiver_id
    functions.add_message(me, receiver_id, content)

    return redirect("/users/{}".format(me))


@app.route("/delete_convo", methods=["POST"])
def delete_convo():
    """delete message thread between two users"""

    user_id = request.form.get("user_id")
    me = session["current_user"]
    
    functions.delete_messages(me, user_id)

    return redirect("/users/{}".format(me))


@app.route("/add_roommate", methods=["POST"])
def add_roommate(): 
    """add a roommate to current listing"""

    listing_id = request.form.get("listing_id")
    user_id = request.form.get("roomie")

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


@app.route("/change_primary", methods=["POST"])
def change_primary(): 
    """change primary lister"""

    listing_id = request.form.get("listing_id")
    user_id = request.form.get("new_primary")
    listing = Listing.query.get(listing_id)
    listing.primary_lister = user_id
    db.session.commit()

    return redirect("/listings/{}".format(listing_id))


@app.route("/login", methods=['POST'])
def login():
    """Log In user"""

    try: 
        user_id = request.form.get("user_id")
        password = request.form.get("password").encode('utf-8')
        user = User.query.get(user_id)
        hashed = user.password.encode('utf-8')
        if password == hashed:
            match = True
        elif bcrypt.hashpw(password, hashed) == hashed:
            match = True
        if match:
            session['current_user'] = user_id
            flash('Successfully logged in as {}'.format(user_id))
            return redirect("/users/{}".format(user_id))
    except: 
        flash("Ya gotta sign up first!")
        return redirect("/")


@app.route("/logout")
def logout():
    """Log Out user."""

    del session['current_user']
    flash('Successfully logged out')

    return redirect("/")


@app.route("/update_state", methods=["POST"])
def update_state():
    """update user's state"""

    state = request.form.get("state")
    user = User.query.get(session["current_user"])
    if user: 
        user.state = state
        db.session.commit()

    return redirect("/")

# AJAX ROUTES
@app.route("/new_messages.json")
def get_new_messages():
    """get new messages"""

    user = User.query.get(session["current_user"])
    partner = request.args.get("sender")
    last = request.args.get("last")
    new_messages = user.get_new_messages(partner, last)
    info = {
        "new_messages": new_messages,
        "partner": partner
    }

    return jsonify(info)


@app.route("/filter_by_price.json")
def filter_by_price():
    """update user's price cap and return listings that match"""

    price_cap = request.args.get("price_cap")
    session["price_cap"] = price_cap

    return functions.get_all_matching_listings()


@app.route("/filter_by_laundry.json")
def filter_by_laundry():
    """only return listings w laundry"""

    session["laundry"] = True

    return functions.get_all_matching_listings()

@app.route("/filter_by_friends.json")
def filter_by_friends():
    """only return listings with mutual friends"""

    session["friends"] = True

    return functions.get_all_matching_listings()


@app.route("/filter_by_pets.json")
def filter_by_pets():
    """only return listings with the correct preference on allowing pets"""

    pets = request.args.get("pets")
    if pets == "yes":
        session["pets"] = True
    else: 
        session["pets"] = False

    return functions.get_all_matching_listings()


@app.route("/filter_by_roommates.json")
def filter_by_roommates():
    """only return listings with roommates or without depending on filter choice"""

    roommates = request.args.get("roommates")
    print roommates
    if roommates == "yes":
        session["roommates"] = True
    else: 
        session["roommates"] = False

    return functions.get_all_matching_listings()


@app.route("/filter_by_neighborhoods.json")
def filter_by_neighborhoods():
    """only return listings in neighborhoods of interest"""

    neighborhoods = request.args.get("neighborhoods")
    neighborhoods = neighborhoods.split("|")
    session["neighborhoods"] = neighborhoods

    return functions.get_all_matching_listings()


@app.route("/filter_by_start_date.json")
def filter_by_start_date():
    """only return listings with start dates within a month"""

    start_dates = request.args.get("start_dates")
    start_dates = start_dates.split("|")
    session["start_dates"] = start_dates

    return functions.get_all_matching_listings()


@app.route("/filter_by_duration.json")
def filter_by_duration():
    """factor duration in"""

    duration = request.args.get("duration")
    session["duration"] = duration

    return functions.get_all_matching_listings()


@app.route("/remove_specific")
def remove_specific():
    """removes clicked filter"""

    f = request.args.get("filter")
    f = f[7:]
    del session[f]

    return functions.get_all_matching_listings()


@app.route("/remove_all_filters.json")
def remove_all_filters():
    """removes all filters"""

    for key in session.keys(): 
        if key != "current_user":
            del session[key]

    print session

    return functions.get_all_matching_listings()


@app.route("/get_all_listings.json")
def get_all_listings_json():
    """get all active listings in a user's state"""

    return functions.get_all_matching_listings()


@app.route("/friend_user", methods=["POST"])
def friend_user():
    """add user as friends"""

    user_id = request.form.get("user_id")
    me = session["current_user"]

    functions.add_friendship(user_id, me)

    info = {
    "friends": True,
    "user_id": user_id
    }

    return jsonify(info)


@app.route("/favorite_listing", methods=["POST"])
def favorite_listing():
    """mark listing as favorite"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    functions.add_favorite(user_id, listing_id)
    info = {
    "favorite": True, 
    "listing_id": listing_id
    }

    return jsonify(info)


@app.route("/unfavorite_listing", methods=["POST"])
def unfavorite_listing():
    """mark listing as not favorite"""

    listing_id = request.form.get("listing_id")
    user_id = session["current_user"]

    functions.delete_favorite(user_id, listing_id)
    info = {
    "favorite": False,
    "listing_id": listing_id
    }

    return jsonify(info)


@app.route("/unlist_listing", methods=["POST"])
def deactivate(): 
    """take listing off market"""

    listing_id = request.form.get("listing_id")
    listing = Listing.query.get(listing_id)
    listing.active = False
    db.session.commit()

    info = {
        "listed": listing.active,
        "listing_id": listing_id
    }

    return jsonify(info)


@app.route("/relist_listing", methods=["POST"])
def reactivate(): 
    """put listing on market with new dates"""

    listing_id = request.form.get("listing_id")
    avail_as_of = request.form.get("avail")
    listing = Listing.query.get(listing_id)
    listing.active = True
    listing.avail_as_of = avail_as_of
    print "TEST"
    print listing.avail_as_of
    db.session.commit()
    avail_date = "{}/{}/{}".format(listing.avail_as_of.month, listing.avail_as_of.day, listing.avail_as_of.year)


    info = {
        "listed": listing.active,
        "listing_id": listing_id,
        "avail_date": avail_date
    }
    print info
    return jsonify(info)

@app.route("/listing_active")
def listing_active():
    """return info regarding whether listing is active"""

    listing_id = request.args.get("listing_id")
    print listing_id
    listing = Listing.query.get(listing_id)
    avail_date = "{}/{}/{}".format(listing.avail_as_of.month, listing.avail_as_of.day, listing.avail_as_of.year)


    if listing.active: 
        info = {
        "listing_id": listing_id, 
        "listed": True, 
        "avail_date": avail_date
        }
    else: 
        info = {
            "listing_id": listing_id, 
            "listed": False 
        }

    print info
    return jsonify(info)


@app.route("/deactivate_user", methods=["POST"])
def deactivate_user(): 
    """take user off market"""

    user = User.query.get(session["current_user"])
    user.looking_for_apt = False
    db.session.commit()
    info = {
    "active": user.looking_for_apt
    }
    return jsonify(info);


@app.route("/reactivate_user", methods=["POST"])
def reactivate_user(): 
    """put user back in play"""

    user = User.query.get(session["current_user"])
    user.looking_for_apt = True
    db.session.commit()

    info = {
    "active": user.looking_for_apt
    }
    return jsonify(info);


@app.route("/listing-info.json")
def listing_info(): 
    """returns listing info as JSON"""

    listing_id = request.args.get("listing_id")
    listing = Listing.query.get(listing_id)
    user = User.query.get(session["current_user"])
    friends = functions.friends_in_listing(user, listing)
    friends = [(friend.name, friend.photo) for friend in friends]
    mutuals = functions.mutual_friends_in_listing(user, listing)
    mutuals = [(mutual.name, mutual.photo) for mutual in mutuals]
    start_date = "{}/{}/{}".format(listing.avail_as_of.month, listing.avail_as_of.day, listing.avail_as_of.year)

    info = {
        "price" : listing.price, 
        "start date": start_date, 
        "friends" : friends, 
        "mutuals": mutuals}

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


@app.route("/listings_info.json")
def listing_info_json():
    """takes a list of listing ids and returns info about them"""

    listing_names = request.args.get("listing_names")
    listing_names = listing_names.split("|")

    listings = []
    for listing_name in listing_names:
        listing = Listing.query.get(listing_name)
        listings.append((listing.address, listing.listing_id))

    info = {"addresses" : listings}

    return jsonify(info)


@app.route("/update_state.json", methods=["POST"])
def update_state_json():
    """update user's state"""

    state = request.form.get("state")
    user = User.query.get(session["current_user"])
    user.state = state
    db.session.commit()
    neighborhoods = functions.get_neighborhoods(state)
    neighborhoods = list(neighborhoods)

    info = {"state": state, 
            "neighborhoods": neighborhoods}

    return jsonify(info)
    





if __name__ == "__main__":

    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')


