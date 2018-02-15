from collections import defaultdict
from flask import request, session
from model import User, Listing, UserListing, Favorite, Friendship, Picture, Question, Answer, UserAnswer
from model import connect_to_db, db 

UPLOAD_FOLDER = "static/uploaded_images/"


def get_current_user(): 
	"""if there is a current user in session, query for that user"""

	if "current_user" in session: 
		return User.query.get(session["current_user"])

	else: 
		flash("Please log in!")
		return redirect("/")


def get_neighborhoods():
	"""query for all neighborhoods in db"""

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


def get_all_second_degree_friends(user):
	"""returns second degree friends and the connections"""

	friends_and_mutuals = defaultdict(list)
	first_degrees = set(get_all_friends(user))
	# if user.friends: 
	for friend in user.friends: 
		second_degrees = friend.friends
		for second_degree in second_degrees: 
			if user.user_id != second_degree.user_id and second_degree not in first_degrees:
				friends_and_mutuals[second_degree].append(friend)

	return friends_and_mutuals


def get_all_friends_of_any_degree(user):
	"""returns friends of any degree"""

	friends = set()
	for friend in user.friends: 
		friends.add(friend)
	for friend in user.friends: 
		if user.user_id != friend.user_id:
				friends.add(friend)

	return friends



def get_all_listings_by_friends_of_any_degree(user):
	"""returns all listings by any degree of friends"""

	listings = []
	friends = get_all_second_degree_friends(user)
	for key in friends: 
		listings += key.listings

	return listings



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


def save_photo(photo_name):
	"""gets photo from form, saves to db, returns filepath"""

	photo_name = request.files["{}".format(photo_name)]
	photo_name_path = UPLOAD_FOLDER + photo_name.filename
	photo_name.save(photo_name_path)

	return "../{}".format(photo_name_path)










