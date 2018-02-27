from collections import defaultdict
from flask import request, flash, session, jsonify
from model import User, Listing, UserListing, Favorite, Friendship, Picture, Question, Answer, UserAnswer, Message
from model import connect_to_db, db 
import datetime

UPLOAD_FOLDER = "static/uploaded_images/"


def logged_in():
    """returns true if the user is logged in"""

    return "current_user" in session


def user_in_listing(listing):
    """returns whether the logged in user is associated with a listing"""

    user = User.query.get(session["current_user"])
    if listing in user.listings or listing.primary_lister == user.user_id: 
        return True
    return False


def get_all_matching_listings():
    """checks the user's house search requirements and returns appropriate listings"""

    user = User.query.get(session["current_user"])
    all_listings = Listing.query.all()
    all_listings = [listing for listing in all_listings if listing.active]
    state = user.state
    all_listings = [listing for listing in all_listings if state in listing.address]
    all_listings = [listing for listing in all_listings if not user_in_listing(listing)]

    if all_listings: 
        if "price_cap" in session: 
            all_listings = [listing for listing in all_listings if listing.price < int(session["price_cap"])]

        if "laundry" in session: 
            all_listings = [listing for listing in all_listings if listing.laundry]

        if "friends" in session:
            all_listings = [listing for listing in all_listings if friends_in_listing(user, listing) or mutual_friends_in_listing(user, listing)]

        if "pets" in session:
            if session["pets"] == True:
                all_listings = [listing for listing in all_listings if listing.pets]
            if session["pets"] == False: 
                all_listings = [listing for listing in all_listings if not listing.pets]

        if "roommates" in session:
            if session["roommates"] == True:
                all_listings = [listing for listing in all_listings if listing.users]
            if session["roommates"] == False: 
                all_listings = [listing for listing in all_listings if not listing.users]

        if "neighborhoods" in session: 
            all_listings = [listing for listing in all_listings if listing.neighborhood in session["neighborhoods"]]

        if "start_dates" in session:
            months = [int(month) for month in session["start_dates"]]
            all_listings = [listing for listing in all_listings if listing.avail_as_of.month in months]

        if "duration" in session:
            duration = int(session["duration"])
            all_listings = [listing for listing in all_listings if listing.length_of_rental < duration + 1 and listing.length_of_rental > duration - 1]


    info = {}
    for listing in all_listings: 
        info[listing.listing_id] = {
        "address": listing.address, 
        "photo": listing.main_photo
        }

    return jsonify(info)


def get_neighborhoods(state):
    """returns a list of all neighborhoods in a state"""

    neighborhoods = set()
    
    listings = Listing.query.filter(Listing.address.like('%{}%'.format(state))).all()
    for listing in listings: 
        neighborhoods.add(listing.neighborhood)

    return neighborhoods


def are_friends(user1, user2):
    """returns true if two users are friends"""

    return user1 in user2.friends


def friends_in_listing(user, listing):
    """returns friends if user has friends in listing"""

    friends = []

    for roommate in listing.users: 
        if roommate in user.friends: 
            friends.append(roommate)
    primary = User.query.get(listing.primary_lister)
    
    if primary in user.friends: 
        friends.append(primary)

    return set(friends)


def mutual_friends(user1, user2):
    """returns a set of mutual friends"""

    mutuals = []

    friends1 = user1.friends
    friends2 = user2.friends
    if friends1 and friends2: 
        for friend in friends1: 
            if friend in friends2:
                mutuals.append(friend)

    return set(mutuals)


def mutual_friends_in_listing(user, listing):
    """returns a set of mutual friends in listing"""

    mutuals = []

    for roommate in listing.users: 
        mutuals += mutual_friends(user, roommate)

    primary = User.query.get(listing.primary_lister)
    mutuals += mutual_friends(user, primary)

    return set(mutuals)


def all_friends_in_listing(user, listing):
    """returns a set of friends and friends of friends associated with a listing"""

    friends = set()
    friends = friends | friends_in_listing(user, listing)
    friends = friends | mutual_friends_in_listing(user, listing)

    return list(friends)


def get_all_friends(user):
    """returns list of friends"""

    return user.friends


def get_all_friends_of_any_degree(user):
    """returns friends of any degree"""

    friends = set()
    for friend in user.friends: 
        friends.add(friend)
        for friend_2 in friend.friends: 
            if user.user_id != friend_2.user_id:
                friends.add(friend_2)

    return friends



def get_all_listings_by_friends_of_any_degree(user):
    """returns all listings by any degree of friends"""

    all_listings = Listing.query.all()

    listings = []
    friends = get_all_friends_of_any_degree(user)
    for friend in friends: 
        listings += friend.listings

    for listing in all_listings:
        primary_lister = User.query.get(listing.primary_lister)
        if primary_lister in friends:
            listings.append(listing) 

    return set(listings)



def get_common_answers(user1, user2):
    """takes two users and returns a lit of their common question answers"""

    answers1 = user1.answers
    answers2 = user2.answers

    common_answers = []
    answers = []

    for answer in answers1: 
        if answer in answers2: 
            common_answers.append(answer)

    for answer in common_answers:
        answers.append("{}:  {}".format(answer.question.question, answer.answer))
    return answers



def add_UserListing(user_id, listing_id):
    """add a user to a listing"""

    db.session.add(UserListing(user_id=user_id,
                               listing_id=listing_id))

    db.session.commit()


def delete_UserListing(user_id, listing_id):
    """delete user from a listing"""

    UserListing.query.filter_by(user_id=user_id, listing_id=listing_id).delete()

    db.session.commit()


def add_favorite(user_id, listing_id):
    """add a favorite"""

    db.session.add(Favorite(user_id=user_id,
                               listing_id=listing_id))

    db.session.commit()


def delete_favorite(user_id, listing_id):
    """delete favorite"""

    Favorite.query.filter_by(user_id=user_id, listing_id=listing_id).delete()

    db.session.commit()


def add_friendship(friend_1_id, friend_2_id):
    """add a friendship between two users"""

    db.session.add(Friendship(friend_1_id=friend_1_id,
                               friend_2_id=friend_2_id))

    db.session.add(Friendship(friend_1_id=friend_2_id,
                               friend_2_id=friend_1_id))

    db.session.commit()


def add_message(user_1_id, user_2_id, message):
    """add a message between two users"""

    db.session.add(Message(sender_id=user_1_id,
                               receiver_id=user_2_id, 
                               message=message))

    db.session.commit()


def delete_messages(user_1_id, user_2_id):
    """delete messages between two users"""

    Message.query.filter_by(sender_id=user_1_id, receiver_id=user_2_id).delete()
    Message.query.filter_by(sender_id=user_2_id, receiver_id=user_1_id).delete()

    db.session.commit()


# def get_new_messages(user, partner, last_message):
#     """gets all messages between two people since a certain message"""

#     all_messages = get_messages(user)
#     messages_with_partner = all_messages[partner]
#     new_messages = [message for message in messages_with_partner if int(message[0]) > int(last_message)]

#     return new_messages


# def get_messages(user):
#     """returns a dictionary of a user's sent and received messages"""

#     received_messages = user.received_messages
#     sent_messages = user.sent_messages

#     message_dict = {}

#     for received in received_messages:
#         sender = received.sender_id
#         if sender in message_dict: 
#             message_dict[sender].append((received.message_id, "{}: {}".format(received.sender_id, received.message)))
#         else: 
#             message_dict[sender] = [(received.message_id, "{}: {}".format(received.sender_id, received.message))]
#     for sent in sent_messages:
#         receiver = sent.receiver_id
#         if receiver in message_dict: 
#             message_dict[receiver].append((sent.message_id, "{}: {}".format(sent.sender_id, sent.message)))
#         else: 
#             message_dict[receiver] = [(sent.message_id, "{}: {}".format(sent.sender_id, sent.message))]
#     for partner in message_dict:
#         message_dict[partner] = sorted(message_dict[partner])

#     return message_dict




def save_photo(photo_name):
    """gets photo from form, saves to db, returns filepath"""

    photo_name = request.files["{}".format(photo_name)]
    photo_name_path = UPLOAD_FOLDER + photo_name.filename
    photo_name.save(photo_name_path)

    return "../{}".format(photo_name_path)










