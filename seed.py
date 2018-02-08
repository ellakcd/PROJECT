"""Utility file to seed database"""

import datetime
from sqlalchemy import func
from model import User, Listing, UserListing, Friendship, Picture, Question, Answer, UserAnswer

from model import connect_to_db, db 
from server import app
from sqlalchemy.inspection import inspect



def load_users():
	"""Load users from seed data into database"""

	print "Users"

	#create data
	with open("seed_data/users.txt") as users:
		for row in users:
			user = row.rstrip().split("|")

			kwargs = dict(
			user_id = user[0],
			name = user[1],
			email = user[2],
			password = user[3],
			phone = user[4],
			bio = user[5],
			photo = user[6],
			state = user[7],
			looking_for_apt = user[8])

			for key in kwargs.keys(): 
				if kwargs[key] == "":
					del kwargs[key]

			user = User(**kwargs)
			#add data
			db.session.add(user)
	#commit
	db.session.commit()


def load_listings():
	"""Load listings from seed data into database"""

	print "Listings"

	with open("seed_data/listings.txt") as listings: 
		for row in listings: 
			listing = row.rstrip().split("|")

			kwargs = dict(listing_id = listing[0],
			neighborhood = listing[1],
			address = listing[2],
			price = listing[3],
			avail_as_of = datetime.datetime.strptime(listing[4], "%d-%b-%Y"),
			length_of_rental = listing[5],
			bedrooms = listing[6],
			bathrooms = listing[7],
			laundry = listing[8],
			pets = listing[9],
			description = listing[10],
			main_photo = listing[11],
			active = listing[12])

			for key in kwargs.keys(): 
				if kwargs[key] == "":
					del kwargs[key]

			listing = Listing(**kwargs)

			db.session.add(listing)

	db.session.commit()


def load_user_listings():
	"""Load user-listings from seed data into database"""

	print "User Listings"

	with open("seed_data/user_listings.txt") as user_listings: 
		for user_listing in user_listings: 
			user_listing = user_listing.rstrip()
			user_listing_id, user_id, listing_id = user_listing.split("|")

			user_listing = UserListing(user_listing_id=user_listing_id, 
				user_id=user_id, 
				listing_id=listing_id)

			db.session.add(user_listing)

	db.session.commit()



def load_friendships():
	"""Load friendships from seed data into database"""

	print "Friendships"


	with open("seed_data/friendships.txt") as friendships: 
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

	with open("seed_data/pictures.txt") as pictures: 
		for picture in pictures: 
			picture = picture.rstrip()
			picture_id, listing_id, photo = picture.split("|")

			picture = Picture(picture_id=picture_id, 
				listing_id=listing_id, 
				photo=photo)

			db.session.add(picture)

	db.session.commit()

def load_questions():
	"""Load questions from seed data into database"""

	print "Questions"

	with open("seed_data/questions.txt") as questions: 
		for q in questions: 
			q = q.rstrip()
			question_id, question = q.split("|")

			question = Question(question_id=question_id, 
				question=question)

			db.session.add(question)

	db.session.commit()


def load_answers():
	"""Load answers from seed data into database"""

	print "Answers"

	with open("seed_data/answers.txt") as answers: 
		for ans in answers: 
			ans = ans.rstrip()
			answer_id, question_id, answer = ans.split("|")

			answer = Answer(answer_id=answer_id, 
				question_id=question_id, 
				answer=answer)

			db.session.add(answer)

	db.session.commit()


def load_user_answers():
	"""Load user-answers from seed data into database"""

	print "User Answers"

	with open("seed_data/user_answers.txt") as user_answers: 
		for user_answer in user_answers: 
			user_answer = user_answer.rstrip()
			user_answer_id, user_id, answer_id = user_answer.split("|")

			user_answer = UserAnswer(user_answer_id=user_answer_id, 
				user_id=user_id, 
				answer_id=answer_id)

			db.session.add(user_answer)

	db.session.commit()



"""
A non-class-specific way to update postgresql's autoincrementing primary key
sequences, useful for running after data including primary key values has been
seeded.

Similar to set_val_user_id() from Ratings, but works on all classes in
model.py.

Author: Katie Byers

"""


def update_pkey_seqs():
    """Set primary key for each table to start at one higher than the current
    highest key. Helps when data has been manually seeded."""

    # get a dictionary of {classname: class} for all classes in model.py
    model_classes = db.Model._decl_class_registry

    # loop over the classes
    for class_name in model_classes:

        # the dictionary will include a helper class we don't care about, so
        # skip it
        if class_name == "_sa_module_registry":
            continue

        print
        print "-" * 40
        print "Working on class", class_name

        # get the class itself out of the dictionary
        cls = model_classes[class_name]

        # get the name of the table associated with the class and its primary
        # key
        table_name = cls.__tablename__
        pkey_column = inspect(cls).primary_key[0]
        primary_key = pkey_column.name
        print "Table name:", table_name
        print "Primary key:", primary_key

        # check to see if the primary key is an integer (which are
        # autoincrementing by default)
        # if it isn't, skip to the next class
        if (not isinstance(pkey_column.type, db.Integer) or
            pkey_column.autoincrement is not True):
            print "Not an autoincrementing integer key - skipping."
            continue

        # now we know we're dealing with an autoincrementing key, so get the
        # highest id value currently in the table
        result = db.session.query(func.max(getattr(cls, primary_key))).first()

        # if the table is empty, result will be none; only proceed if it's not
        # (we have to index at 0 since the result comes back as a tuple)
        if result[0]:
            # cast the result to an int
            max_id = int(result[0])
            print "highest id:", max_id

            # set the next value to be max + 1
            query = ("SELECT setval('" + table_name + "_" + primary_key +
                     "_seq', :new_id)")
            db.session.execute(query, {'new_id': max_id + 1})
            db.session.commit()
            print "Primary key sequence updated."
        else:
            print "No records found. No update made."

    # we're done!
    print
    print "-" * 40
    print
    print "Primary key sequences updated!"
    print



if __name__ == "__main__":
	connect_to_db(app)

	db.create_all()


	load_users()
	load_listings()
	load_friendships()
	load_pictures()
	load_questions()
	load_answers()
	load_user_listings()
	load_user_answers()
	update_pkey_seqs()


