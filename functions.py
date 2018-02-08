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

	return mutuals


def mutual_friends_in_listing(user1, listing):
	"""returns a list of mutual friends in listing"""

	mutuals = []

	for user2 in listing.users: 
		print user1
		mutuals += mutual_friends(user1, user2)

	return mutuals

def get_all_friends(user):
	"""returns list of friends"""

	return user.friends


def get_all_second_degree_friends(user):
	"""returns second degree friends and the connections"""

	friends_and_mutuals = {}
	# if user.friends: 
	for friend in user.friends: 
		second_degrees = friend.friends
		for second_degree in second_degrees: 
			# if user != second_degree and second_degree not in get_all_friends(user):
			friends_and_mutuals[second_degree.user_id] += friend

	return friends_and_mutuals

