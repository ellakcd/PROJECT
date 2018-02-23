from collections import defaultdict
from flask import request, session
from model import User, Listing, UserListing, Favorite, Friendship, Picture, Question, Answer, UserAnswer, Message
from model import connect_to_db, db 

UPLOAD_FOLDER = "static/uploaded_images/"


def logged_in():
    """returns true if the user is logged in"""

    return "current_user" in session


def get_current_user(): 
    """if there is a current user in session, query for that user"""

    if "current_user" in session: 
        return User.query.get(session["current_user"])

    else: 
        flash("Please log in!")
        return redirect("/")

def user_in_listing(listing):
    """returns whether the logged in user is associated with a listing"""

    user = get_current_user()
    if listing in user.listings or listing.primary_lister == user.user_id: 
        return True
    return False

def get_listings(state, neighborhoods, price_cap, live_alone, start_date):
    """get all listings that meet search filters"""

    # If they've selected specific neighborhoods, make a list of all listings with those neighborhoods
    if neighborhoods: 
        for neighborhood in neighborhoods:
            listings = Listing.query.filter(Listing.neighborhood == neighborhood).all()

            # In case multiple states have neighborhoods with the same photo_name
            right_state = Listing.query.filter(Listing.address.like('%{}%'.format(state))).all()
            for listing in listings:
                if listing not in right_state:
                    listings.remove(listing)
    # otherwise, start with a list of all houses in the right state
    else: 
        listings = Listing.query.filter(Listing.address.like('%{}%'.format(state))).all()

    
    listings = [listing for listing in listings if listing.price <= price_cap and str(listing.avail_as_of) >= start_date]
    listings = [listing for listing in listings if not user_in_listing(listing)]
    
    if live_alone == "yes": 
        listings = [listing for listing in listings if not listing.users]
    elif live_alone == "no":
        listings = [listing for listing in listings if not listing.users]
    listings = [listing for listing in listings if listing.active]
    return listings



def get_neighborhoods():
    """query for all neighborhoods currently in db"""

    neighborhoods = db.session.query(Listing.neighborhood).group_by(Listing.neighborhood).all()
    neighborhoods = [neighborhood[0] for neighborhood in neighborhoods]
    return neighborhoods


def are_friends(user1, user2):
    """returns true if two users are friends"""

    return user1 in user2.friends



def friends_in_listing(user1, listing):
    """returns friends if user has friends in listing"""

    friends = []

    for user2 in listing.users: 
        if user1 in user2.friends: 
            friends.append(user2)

    return friends


def mutual_friends(user1, user2):
    """returns a list of mutual friends"""

    mutuals = []

    friends1 = user1.friends
    friends2 = user2.friends
    # if friends1 and friends2: 
    for friend in friends1: 
        if friend in friends2:
            mutuals.append(friend)

    return set(mutuals)


def mutual_friends_in_listing(user1, listing):
    """returns a list of mutual friends in listing"""

    mutuals = []

    for user2 in listing.users: 
        mutuals += mutual_friends(user1, user2)

    return set(mutuals)


def get_all_friends(user):
    """returns list of friends"""

    return user.friends


# def get_all_second_degree_friends(user):
#     """returns second degree friends and the connections"""

#     friends_and_mutuals = defaultdict(list)
#     first_degrees = set(get_all_friends(user))
#     # if user.friends: 
#     for friend in user.friends: 
#         second_degrees = friend.friends
#         for second_degree in second_degrees: 
#             if user.user_id != second_degree.user_id and second_degree not in first_degrees:
#                 friends_and_mutuals[second_degree].append(friend)

#     return friends_and_mutuals


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

    listings = []
    friends = get_all_friends_of_any_degree(user)
    for friend in friends: 
        listings += friend.listings

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
    

# def get_convo_partners(user):
#     """returns a list of user_ids of people user has convos with"""

#     received_messages = user.received_messages
#     sent_messages = user.sent_messages
#     partners = set()
#     for received in received_messages:
#         partners.add(received.sender_id)
#     for sent in sent_messages:
#         partners.add(sent.receiver_id)
#     partners = [str(partner) for partner in partners]

#     return partners


# def get_full_convo(user, partner):
#     """returns full text of convo between two users"""

#     messages = []
#     messages.append(user.received_messages)
#     messages.append(user.sent_messages)
#     messages = [message for message in messages if message.receiver_id is partner or messages.sender_id is partner]
#     messages = [(message.message_id, "{}: {}".format(message.sender_id, message.message)) for message in messages]

    # return sorted(messages)


def get_new_messages(user, partner, last_message):
    """gets all messages between two people since a certain message"""

    print last_message
    all_messages = get_messages(user)
    messages_with_partner = all_messages[partner]
    print messages_with_partner
    new_messages = [message for message in messages_with_partner if int(message[0]) > int(last_message)]

    return new_messages


def get_messages(user):
    """returns a dictionary of a user's sent and received messages"""

    received_messages = user.received_messages
    sent_messages = user.sent_messages

    message_dict = {}

    for received in received_messages:
        sender = received.sender_id
        if sender in message_dict: 
            message_dict[sender].append((received.message_id, "{}: {}".format(received.sender_id, received.message)))
        else: 
            message_dict[sender] = [(received.message_id, "{}: {}".format(received.sender_id, received.message))]
    for sent in sent_messages:
        receiver = sent.receiver_id
        if receiver in message_dict: 
            message_dict[receiver].append((sent.message_id, "{}: {}".format(sent.sender_id, sent.message)))
        else: 
            message_dict[receiver] = [(sent.message_id, "{}: {}".format(sent.sender_id, sent.message))]
    for partner in message_dict:
        message_dict[partner] = sorted(message_dict[partner])


    # message_dict = {}

    # for sender in senders_and_messages:
    #     message_dict[sender] = []
    #     for message in senders_and_messages[sender]:
    #         message_dict[sender].append((message[0], "{}: {}".format(message[1], message[2])))

    return message_dict


    # received_messages = user.received_messages
    # sent_messages = user.sent_messages

    # convos_and_messages = {}

    # for received in received_messages:
    #     partner = received.sender_id
    #     if partner in convos_and_messages: 
    #         convos_and_messages[partner].append((received.message_id, received.sender_id, received.message))
    #     else: 
    #         convos_and_messages[partner] = [(received.message_id, received.sender_id, received.message)]
    # for sent in sent_messages:
    #     partner = sent.receiver_id
    #     if partner in convos_and_messages: 
    #         convos_and_messages[partner].append((sent.message_id, sent.sender_id, sent.message))
    #     else: 
    #         convos_and_messages[partner] = [(sent.message_id, sent.sender_id, sent.message)]
    # for sender in convos_and_messages:
    #     convos_and_messages[partner] = sorted(convos_and_messages[sender])


    # message_dict = {}

    # for partner in convos_and_messages:
    #     message_dict[partner] = []
    #     for message in convos_and_messages[partner]:
    #         message_dict[partner].append({"message_id" : message[0], "text" : "{}: {}".format(message[1], message[2])})

    # return message_dict


def save_photo(photo_name):
    """gets photo from form, saves to db, returns filepath"""

    photo_name = request.files["{}".format(photo_name)]
    photo_name_path = UPLOAD_FOLDER + photo_name.filename
    photo_name.save(photo_name_path)

    return "../{}".format(photo_name_path)










