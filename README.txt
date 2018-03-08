RoomMatch

Summary

	RoomMatch is a housing app based around mutual friends.  Wouldn't you feel more comfortable living with someone who was fewer degrees of    separation away?  Using SQL databases, RoomMatch keeps track of user info, listing info, and connections to bring a personal dimension to the housing search.  It uses Python backend, Flask routes, Javascript for informational pop ups and real time chat, and Google Maps to locate listings in space.

Setup

	Clone this repo
		https://github.com/ellakcd/PROJECT.git

    Launch and activate a virtual environment

        $ virtualenv env
        $ source env/bin/activate

    Install Python 2.7

    pip install requirements
        
        $ pip install -r requirements.txt


    Create and seed the database

        $ createdb roommatch
        $ python model.py
        $ python seed.py

    Launch server

        $ python server.py

    View app at:
    
        http://localhost:5000/


Test it out!

    Register as a new user to:
    	- create your own profile (don't worry - your password is encrypted)
    	- friend other users and see listings by friends and friends of friends
        - browse listings based on your filters - try favoriting and unfavoriting 
        - create your own listing - try unlisting it and listing for different dates
        - message other users
        - hover over listings and user for info about them
        - click on map links to be taken to listing locations on Google Maps


    Login as Harry Potter to play around with features:

        User ID: HP 
        password: password1

        Features to try:
        - browse listings based on your filters - try favoriting and unfavoriting 
        - create your own listing - try unlisting it and listing for different dates 
        - hover over listings and user for info about them


    Login as two users in seperate windows (one regular one incognito) to play around with live chat: 

    	User ID: RG
    	password: password6

    	Test out chat: 
    	- view your own profile in each window
    	- send messages to eachother and have a conversation with yourself! 



Tech Stack:

	Backend: 
	- Python, Flask, SQLAlchemy, PostgreSQL
	Frontend: 
	- Jinja2, HTML, CSS, Javascript, JQuery, AJAX
	APIs:
	- Google Maps 













