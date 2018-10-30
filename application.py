import os
import requests
from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import exc

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#Stores the variables from register.html
request_list = ["password", "email", "first_name", "last_name", 
				"dob", "country","author", "book",]				

def get_form_data(request_list):
	'''retrieves form data according to variables in 
	request_list and stores them in return_list'''
	reg_success = True
	return_list = []
	reg_dict = {}
	color_dict = {}
	for e in request_list:
		temp = request.form.get(e)
		# if a value retrieved from the form is blank...
		if temp == "":
			# wipe the dict
			reg_dict[e] = ""
			# change color of that entry form to be red
			color_dict[e] = 'background-color:#ffd0c4'
			# registration has failed so change to false
			if reg_success == True:
				reg_success = False
		else:
			# if not blank append a key, value to return_list
			reg_dict[e] = temp
			return_list.append(temp)
	# list will return false to show reg has failed
	if reg_success == False:
		return_list = False
	#stores all values retrieved from form as key,value pairs in a dict
	session["temp_reg"] = reg_dict
	session["colors"] = color_dict
	return return_list

@app.route("/", methods=["GET"])
def index():
	'''Login page'''
	session.clear()
	return render_template("index.html")

@app.route("/#", methods=["POST"])
def logout():
	'''clear out session variables and return to login page'''
	session.clear()
	return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
	'''register user'''
	msg = "Join the Scrolled clan"
	# change display if the user has registered successfully or not
	registered = False
	# determines where user's directed after success/unsuccessful login
	url = 'index'
	# text on page changed depending on successful registration attempt
	msg_2 = "At Scrolled we are scrolled"
	# will store details retrieved from html form
	details = ""
	# stores color used for html
	colors = ""

	if request.method == "POST":
		return_list = get_form_data(request_list)
		# if some of the values retrieved were blank...
		if return_list == False:
			msg_2 = "Please enter in all details requested"
			details = session["temp_reg"]
			colors = session["colors"]
			# wipe the session dicts to be used again later
			session["temp_reg"] = ""
			session["colors"] = 'background-color:#ffd0c4'

		else:
			try:
				# insert values retrieved from form into db
				db.execute('''INSERT INTO user_logins (password, email) 
							VALUES 
							(:password, :email)''',
							{"password":return_list[0], 
							"email": return_list[1]})
				db.commit()
				fori_id = db.execute('''SELECT user_id FROM user_logins
										 WHERE email = :email''',
										 {"email": return_list[1]}).fetchone()
			# if unique value of email already in db..
			except exc.SQLAlchemyError:
				#... display error text, color email form in red
			 	msg = "Email already registered... "
			 	colors = {'email': 'background-color:#ffd0c4'}
			 	#...have html form display values previously entered
			 	details = session["temp_reg"]
			 	#... modify look of template via jina 
			 	#... because registration unsuccessful
			 	registered = False

			else:
				db.execute('''INSERT INTO user_details 
							(first_name, last_name, dob, country, user_id) 
							  VALUES 
							(:first_name, :last_name, :dob, :country, :user_id)''',
							{"first_name":return_list[2], 
							"last_name": return_list[3],
							"dob": return_list[4],
							"country": return_list[5],
							"user_id":fori_id.user_id})
				db.commit()
				#retrieve ID of user who has just registered...
				user_id = db.execute('''SELECT user_id FROM user_logins 
										WHERE email = :email''',
										{"email": return_list[1]}).fetchone()
				#... and log them in
				session["user_id"] = user_id.user_id
				#... assign str to be used in html to alert user
				msg = "Registration Successful"
				registered = True
				url = 'home'

	register_info = {	"msg":msg,
						"msg_2":msg_2,
						"registered":registered,
						"url":url,
						"details":details,
						"color":colors }

	return render_template("register.html", register_info=register_info)

			
@app.route("/home", methods=["GET"])
def home():
	'''
	Display logged in users favourite authors and books 
	and welcome them by name
	'''
	rows = db.execute("""SELECT book, author FROM user_likes  
		WHERE user_id = :user_id""",
		{"user_id":session["user_id"]}).fetchall()

	deets = db.execute("""SELECT first_name FROM user_details 
		WHERE user_id = :user_id""",
		{"user_id":session["user_id"]}).fetchone()

	return render_template("home.html", rows=rows, name=deets.first_name)

@app.route("/about", methods=["GET"])
def about():
	'''render page for user to update favourite author and book'''
	return render_template("about.html")
	
@app.route("/about", methods=["POST"])
def update_about():
	'''retrieve favourites from form to add to db'''
	return_list = get_form_data(request_list)
	db.execute('''INSERT INTO user_likes (author, book, user_id) 
					VALUES (:author, :book, :user_id)''',
					{"author":return_list[6], "book": return_list[7],
					 "user_id":session["user_id"]})
	db.commit()
	return render_template("about.html")	


@app.route("/", methods=["POST"])
def login():
	'''
	Compare email + password retrieved from form to db to determine 
	if they match. If matching, session["user_id"] will be assigned 
	the id retrieved from the db so that the site will display info 
	corresponding to the user
	'''
	email = request.form.get("email")
	password = request.form.get("password")

	# grab email if email and password are a match in db
	logins = db.execute('''SELECT email FROM user_logins 
							WHERE email = :email 
							and password = :password''',
	     					{"email": email, "password": password}).fetchone()

	# try and log into user, load name up on next page if successful...
	# ...reload page with error if not.
	# - error will be caused by logins.email being None because... 
	# ...None were found
	
	usr_name = db.execute("""SELECT * FROM user_details 
							JOIN user_logins
							ON user_logins.user_id = user_details.user_id
							WHERE email = :email """,
							{"email":logins.email}).fetchone() 
	session["user_id"] = usr_name.user_id
	return home()

	fail = "LogIn failed. Password or Email not recognised."
	return render_template("index.html", fail=fail)

@app.route("/home", methods=["GET", "POST"])
def search():
	'''Search through db for anything similar to user input in form'''
	try:
		entry = request.form.get("search")
		entry = "%" + entry + "%"
		rows = db.execute('''SELECT * FROM books WHERE book_name 
							LIKE :search or author LIKE :search 
							or ISBN LIKE :search''',
							{"search":entry}).fetchall()
	except Exception:
	 	rows=[]
	return render_template("results.html", rows=rows)



@app.route("/results", methods=["POST", "GET"])
def get_book():
	'''
	Retrieve info on clicked on search result and render to book_page
	'''
	
	if request.method == "POST":
		# Convert the clicked on item in search results into a list
		row = request.form.get('clicked')
		row = row.split(",")
	else:
		# error handling for if page is refreshed for some reason...
		# - assigns row variable also stored in session
		row = session["clicked"]["row"]
	book_id = row[0][1:]
	isbn = row[1][2:-1]

	rating = "Not yet rated"
	review = "Not yet reviewed"
	# used to make sure user can only submit one review of each product
	# - subsequent reviews will replace the other
	already_reviewed = False	
	gr_avg = "None found"
	#retrieve 'Good Reads' ratings and jsonify it found
	res = requests.get("https://www.goodreads.com/book/review_counts.json", 
						params={"key": "sTyqqTgOkb6g67c1oDPmzA", 
						"isbns": isbn})
	if res.status_code != 404:
		gr_avg = res.json()
		gr_avg = gr_avg["books"][0]["average_rating"]


	reviews = db.execute("""SELECT * FROM user_details JOIN reviews
				ON reviews.reviewer_id = user_details.user_id
				WHERE book_id = :book_id """, {"book_id":book_id}).fetchall()
	
	avg_rating = db.execute('''SELECT AVG(rating) FROM reviews 
		WHERE book_id = :book_id''', {"book_id":book_id}).fetchone()

	for e in reviews:
		# if reveiws owned by logged in user assign to variables used... 
		# in session dict
		if e.reviewer_id == session["user_id"]:
			rating = e.rating
			review = e.review
			# ensure no new review of item will be posted... 
			# ...unless user presses resubmit
			already_reviewed = True
	
	if avg_rating.avg != None:
		avg_rating = "{0:.2f}".format(avg_rating.avg)
	else:
		avg_rating = "Not yet rated"

	# dict to store all retrieved data to be used later... 
	# ...without need for more sql queries
	session["clicked"] = { "row": row,
						   "rating": rating,
						   "review": review,
						   "reviews": reviews,
						   "book_id": book_id,
						   "already_reviewed":already_reviewed,
						   "avg_rating":avg_rating,
						   "gr_avg":gr_avg }

	return render_template("book_page.html", book_info=session["clicked"])


@app.route("/book_page", methods=["POST", "GET"])
def rate():
	'''User rates and retrieves items which is then stored in db'''
	if request.method == "GET":
		return render_template("book_page.html", book_info=session["clicked"])
	elif request.method == "POST":
		rating = int(request.form.get("usr_rating"))
		review = request.form.get("texty")
		# the book id of the item that was clicked on in results
		book_id = int(session["clicked"]["book_id"])
		# remove any previous review submitted and replace with new one
		db.execute('''DELETE FROM reviews WHERE book_id = :book_id 
						and reviewer_id = :reviewer_id''', 
						{"book_id":book_id, 
						"reviewer_id":session["user_id"]})
		db.execute('''INSERT INTO reviews 
						(book_id, rating, review, reviewer_id) 
						VALUES (:book_id, :rating, :review, :reviewer_id)''', 
						{"book_id":book_id, "rating":rating, 
						"review": review, "reviewer_id":session["user_id"]})
		db.commit()
		# update db with avg rating
		avg_rating = db.execute('''SELECT AVG(rating) FROM reviews 
									WHERE book_id = :book_id''', 
									{"book_id":book_id}).fetchone()
		avg_rating = "{0:.2f}".format(avg_rating[0])
		db.execute('''UPDATE books  SET avg_rating = :avg_rating 
						WHERE book_id = :book_id''', 
						{"avg_rating":avg_rating,"book_id":book_id})
		# to be used for api requests and books db
		r_count = db.execute('''SELECT books.isbn, COUNT(*) 
								FROM reviews 
								JOIN books 
								ON reviews.book_id = books.book_id 
								GROUP BY isbn''').fetchone()
		db.execute('''UPDATE books SET review_count = :r_count 
						WHERE book_id = :book_id''', 
						{"r_count":r_count.count,"book_id":book_id})	
		db.commit()
		# this is retrieved again from db so the page displays up to... 
		# ...date info (e.g info after user has submitted)
		reviews = db.execute("""SELECT * FROM user_details JOIN reviews
				ON reviews.reviewer_id = user_details.user_id
				WHERE book_id = :book_id """, 
				{"book_id":book_id}).fetchall()

		session["clicked"].update({"rating":rating,
									"reviews":reviews,
									"review":review,
									"avg_rating":avg_rating,
									"already_reviewed":True })
														
		return render_template("book_page.html", book_info=session["clicked"])

@app.route("/api/<string:isbn>", methods=["GET"])
def flight_api(isbn):
	'''API for users to retrieve json data'''
	rows = db.execute('''SELECT * FROM books
						WHERE ISBN = :ISBN''', 
						{"ISBN": isbn}).fetchone()
	if rows == None:
		return jsonify ({
			"error":"No results found for given ISBN: %s" % (isbn)
			}), 422
	else:
		return jsonify ({
			"title":rows.book_name,
			"Author":rows.author,
			"ISBN":rows.isbn,
			"year":rows.year,
			"avg_rating":rows.avg_rating,
			"review_count":rows.review_count
			})