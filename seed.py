"""Utility file to seed database"""

import datetime
from sqlalchemy import func
from model import User, Listing, UserListing, Friendship, Picture, Question, Answer, UserAnswer

from model import connect_to_db, db 
from server import app


def load_users():
	"""Load users from seed data into database"""

	print "Users"

	#Delete all rows in table so can strart from scratch if need to repopulate
	User.query.delete()

	#create data
	with open("seed_data/users.txt") as users:
		for user in users:
			user = user.rstrip()
			user_id, user_name, name, email, password, phone, bio, photo, city = users.split("|")

			user = User(user_id=user_id,
				user_name=user_name,
				name=name,
				email=email,
				password=password, 
				phone=phone, 
				bio=bio, 
				photo=photo, 
				city=city
				)
			#add data
			db.session.add(user)
	#commit
	db.session.commit()


def load_listings():
	"""Load listings from seed data into database"""

	print "Listings"

	Listing.query.delete()

	with open("seed_data/listings.txt") as listings: 
		for listing in listings: 
			listing = listing.rstrip().split("|")

			listing_id = listing[0]
			neighborhood = listing[1]
			address = listing[2]
			price = listing[3]
			avail_as_of = datetime.datetime.strptime(listing[4], "%d-%b-%Y")
			length_of_rental = listing[5]
			bedrooms = listing[6]
			bathrooms = listing[7]
			laundry = listing[8]
			pets = listing[9]
			description = listing[10]

			listing = Listing(listing_id=listing_id, 
				neighborhood=neighborhood,
				address=address, 
				price=price, 
				avail_as_of=avail_as_of, 
				length_of_rental=length_of_rental, 
				bedrooms=bedrooms, 
				bathrooms=bathrooms, 
				laundry=laundry, 
				pets=pets, 
				description=description)

			db.session.add(listing)

	db.session.commit()


def load_user_listings():
	"""Load user-listings from seed data into database"""

	print "User Listings"

	UserListing.query.delete()

	with open("seed_data/user_listings.txt") as user_listings: 
		for user_listing in user_listings: 
			user_listing = user_listing.rstrip()
			user_listing_id, user_id, listing_id = user_listing.split("|")

			user_listing = UserListing(user_listing_id=user_listing_id, 
				user_id=user_id, 
				listing_id=listing_id)

			db.session.add(user_listing)

	db.session.commit()



# def load_reqs():
# 	"""Load user requirements from seed data into database"""

# 	Req.query.delete()

# 	with open("seed_data/reqs.txt") as reqs: 
# 		for req in reqs: 
# 			req = req.rstrip()
# 			req_id, user_id, city, max_price, start_date, length_of_rental = req.split("|")

# 			req = Req(req_id=req_id, 
# 				user_id=user_id, 
# 				city=city, 
# 				max_price=max_price, 
# 				start_date=start_date, 
# 				length_of_rental=length_of_rental)

# 			db.session.add(req)

# 	db.session.commit()


# def load_areas():
# 		"""Load areas from seed data into database"""

# 	Area.query.delete()

# 	with open("seed_data/area.txt") as areas: 
# 		for area in areas: 
# 			area = area.rstrip()
# 			area_id, user_id, area = area.split("|")

# 			area = Area(area_id=area_id, 
# 				user_id=user_id, 
# 				area=area)

# 			db.session.add(area)

# 	db.session.commit()



def load_friendships():
	"""Load friendships from seed data into database"""

	print "Friendships"

	Friendship.query.delete()

	with open("seed_data/friendship.txt") as friendships: 
		for friendship in friendships: 
			friendship = friendship.rstrip()
			friendship_id, friend_1_id, friend_2_id = friendship.split("|")

			friendship = Friendship(friendship_id=friendship_id, 
				friend_1_id=friend_1_id, 
				friend_2_id=friend_2_id)

			db.session.add(friendship)

	db.session.commit()


def load_pictures():
	"""Load pictures from seed data into database"""

	print "Pictures"

	Picture.query.delete()

	with open("seed_data/pictures.txt") as pictures: 
		for picture in pictures: 
			picture = picture.rstrip()
			picture_id, listing_id, photo = question.split("|")

			picture = Picture(picture_id=picture_id, 
				listing_id=listing_id, 
				photo=photo)

			db.session.add(picture)

	db.session.commit()

def load_questions():
	"""Load questions from seed data into database"""

	print "Questions"

	Question.query.delete()

	with open("seed_data/question.txt") as questions: 
		for question in questions: 
			question = question.rstrip()
			question_id, question = question.split("|")

			question = Question(question_id=question_id, 
				question=question)

			db.session.add(question)

	db.session.commit()


def load_answers():
	"""Load answers from seed data into database"""

	print "Answers"

	Answer.query.delete()

	with open("seed_data/answers.txt") as answers: 
		for answer in answers: 
			answer = answer.rstrip()
			answer_id, question_id, answer = answer.split("|")

			answer = Answer(answer_id=answer_id, 
				question_id=question_id, 
				answer=answer)

			db.session.add(answer)

	db.session.commit()


def load_user_answers():
	"""Load user-answers from seed data into database"""

	print "User Answers"

	UserAnswer.query.delete()

	with open("seed_data/user_answer.txt") as user_answers: 
		for user_answer in user_answers: 
			user_answer = user_answer.rstrip()
			user_answer_id, user_id, answer_id = user_answer.split("|")

			user_answer = UserAnswer(user_answer_id=user_answer_id, 
				user_id=user_id, 
				answer_id=answer_id)

			db.session.add(user_answer)

	db.session.commit()



if __name__ == "__main__":
	connect_to_db(app)

	db.create_all()

	load_users()
	load_listings()
	load_user_listings()
	load_friendships()
	# load_pictures()
	load_questions()
	load_answers()
	load_user_answers()


