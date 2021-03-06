"""Models and database functions for RooMatch"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""Model definitions"""


class User(db.Model):
    """Users of rental site"""

    __tablename__ = "users"

    user_id = db.Column(db.String(20), unique=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    bio = db.Column(db.String(100), nullable=True, default="I keep it mysterious...")
    photo = db.Column(db.String(100), nullable=True, default="static/images/default.jpg")
    state = db.Column(db.String(100), nullable=True, default="I move around a lot")
    venmo = db.Column(db.String(100), nullable=True)
    looking_for_apt = db.Column(db.Boolean, nullable=False, default=True)

    listings = db.relationship("Listing", 
                                secondary="user_listings", 
                                backref="users")

    answers = db.relationship("Answer", 
                                secondary="user_answers", 
                                backref="users")

    friends = db.relationship("User", 
                                secondary="friendships",
                                primaryjoin="User.user_id==Friendship.friend_1_id", 
                                secondaryjoin="User.user_id==Friendship.friend_2_id")

    sent_messages = db.relationship("Message", 
                                    foreign_keys="Message.sender_id",
                                    backref=db.backref("sender"))

    received_messages = db.relationship("Message", 
                                    foreign_keys="Message.receiver_id",
                                    backref=db.backref("receiver"))

    favorites = db.relationship("Listing", 
                                secondary="favorites")


    def get_new_messages(self, partner, last_message):
        """gets all messages between two people since a certain message"""

        all_messages = self.get_messages()
        messages_with_partner = all_messages[partner]
        new_messages = [message for message in messages_with_partner if int(message[0]) > int(last_message)]

        return new_messages


    def get_messages(self):
        """returns a dictionary of a user's sent and received messages"""

        received_messages = self.received_messages
        sent_messages = self.sent_messages

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

        return message_dict



    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<User name={} user_id={}>".format(self.name, self.user_id)


class Listing(db.Model):
    """Listings on rental site"""

    __tablename__ = "listings"

    listing_id = db.Column(db.String(20), unique=True, primary_key=True)
    primary_lister = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)
    main_photo = db.Column(db.String(100), nullable=True, default="static/images/default.jpg")
    neighborhood = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    avail_as_of = db.Column((db.DateTime), nullable=False)
    length_of_rental = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    laundry = db.Column(db.Boolean, nullable=False, default=False)
    pets = db.Column(db.Boolean, nullable=False, default=False)
    description = db.Column(db.String(200), nullable=True, default="Come see for yourself!")
    active = db.Column(db.Boolean, nullable=False, default=True)

    user_listings = db.relationship("UserListing",
                                    backref="listings")


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Listing address={} price={}>".format(self.address, self.price)


class UserListing(db.Model):
    """Users and listings on rental site"""

    __tablename__ = "user_listings"

    user_listing_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.listing_id"), nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<User Listing id={}>".format(self.user_listing_id)


class Favorite(db.Model):
    """Users and favorite listings on rental site"""

    __tablename__ = "favorites"

    favorite_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.listing_id"), nullable=False)
    

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Favorite id={}>".format(self.favorite_id)


class Message(db.Model):
    """messages between users"""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sender_id = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)
    receiver_id = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)
    message = db.Column(db.String(500), nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Message id={} message={}>".format(self.message_id, self.message)


class Picture(db.Model):
    """Pics of listings"""

    __tablename__ = "pictures"

    picture_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.listing_id"), nullable=False)
    photo = db.Column(db.String(200), nullable=False)

    listing = db.relationship("Listing", backref="photos")

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Picture id={} listing={} photo={}>".format(self.picture_id, self.listing_id, self.photo)


class Friendship(db.Model):
    """Friendship between users"""

    __tablename__ = "friendships"

    friendship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    friend_1_id = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)
    friend_2_id = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)


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


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Answer {}>".format(self.answer)


class UserAnswer(db.Model):
    """User's answer to multiple choice question"""

    __tablename__ = "user_answers"

    user_answer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey("users.user_id"), nullable=False)
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
 



