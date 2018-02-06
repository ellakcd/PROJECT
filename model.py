"""Models and database functions for RooMatch"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""Model definitions"""


class User(db.Model):
	"""Users of rental site"""

	__tablename__ = "users"

	user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_name = db.Column(db.String(100), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(15), nullable=False)
	phone = db.Column(db.Integer, nullable=False)
	bio = db.Column(db.String(100), nullable=True, default="I keep it mysterious...")
	photo = db.Column(db.String(100), nullable=True, default="/default.jpg")
	city = db.Column(db.String(100), nullable=True, default="I move around a lot")

	listings = db.relationship("Listing", 
								secondary="user_listings", 
								backref="users")

	answers = db.relationship("Answers", 
								secondary="user_answers", 
								backref="users")

	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<User name={} user_id={}>".format(self.name, self.user_id)


class Listing(db.Model):
	"""Listings on rental site"""

	__tablename__ = "listings"

	listing_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	# lister_id = db.Column(db.Integer, db.ForeignKey(user.user_id), nullable=False)
	# CHANGE TO LAT LONG?
	neighborhood = db.Column(db.String(100), nullable=False)
	address = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	avail_as_of = db.Column((db.DateTime), nullable=False)
	length_of_rental = db.Column(db.Integer, nullable=False)
	bedrooms = db.Column(db.Integer, nullable=False)
	bathrooms = db.Column(db.Integer, nullable=False)
	laundry = db.Column(db.Boolean, nullable=False)
	pets = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String(200), nullable=True, default="Come see for yourself!")

	users = db.relationship("User",
							secondary="user_listings", 
							backref="users")

	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<Listing address={} price={}>".format(self.address, self.price)


class UserListing(db.Model):
	"""Users and listings on rental site"""

	__tablename__ = "user-listings"

	user_listing_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	listing_id = db.Column(db.Integer, db.ForeignKey("listings.listing_id"), nullable=False)

	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<User Listing id={}>".format(self.user_listing_id)


class Picture(db.Model):
	"""Pics of listings"""

	__tablename__ = "pictures"

	picture_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	listing_id = db.Column(db.Integer, db.ForeignKey("listings.listing_id"), nullable=False)
	photo = db.Column(db.String(200), nullable=False)

	listing = db.relationship("Listing", backref="photos")

	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<Picture id={} listing={}>".format(self.picture_id, self.listing_id)


class Friendship(db.Model):
	"""Friendship between users"""

	__tablename__ = "friendships"

	friendship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	friend_1_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	friend_2_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

	user = db.relationship("User", backref="friendships")

	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<Friendship id={}>".format(self.friendship_id)


class Question(db.Model):
	"""Compatibility Question"""

	__tablename__ = "questions"

	question_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	question = db.Column(db.String(200), nullable=False)


	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<Question {}>".format(self.question)


class Answer(db.Model):
	"""Answer to multiple choice question"""

	__tablename__ = "answers"

	answer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	question_id = db.Column(db.Integer, db.ForeignKey("questions.question_id"), nullable=False)
	answer = db.Column(db.String(200), nullable=False)

	question = db.relationship("Question", backref="answers")

	users = db.relationship("Answer", 
							secondary="user_answers", 
							backref="answers")

	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<Answer {}>".format(self.answer)


class UserAnswer(db.Model):
	"""User's answer to multiple choice question"""

	__tablename__ = "user_answers"

	user_answer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	answer_id = db.Column(db.Integer, db.ForeignKey("answers.answer_id"), nullable=False)

	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "<User Answer {}>".format(self.user_answer_id)



# Helper Functions

def connect_to_db(app):
	"""Connect the database to our Flask app"""

	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///roommatch'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.app = app
	db.init_app(app)


if __name__ == "__main__":
	from server import app
	connect_to_db(app)
	print "Connected to DB."
 



