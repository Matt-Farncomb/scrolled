import os

from flask import Flask, session, render_template, request
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

books = []

#details=[]
#Stores the variables from register.html
request_list = ["password", "email", "first_name", "last_name", 
				"dob", "country","author", "book",]

#stores the form data from get_form_data
# return_list = []

fail = "LogIn failed. Password or Email not recognised."				

#retrieves form data according to variables in request_list and stores them in return_list
def get_form_data(request_list):
		return_list = []
		for e in request_list:
			return_list.append(request.form.get(e))
		return return_list

@app.route("/", methods=["GET"])
def index():
	
	    #book = request.form.get("book")
	    #books.append(book)

	    ###Currently as a test grabs password off the entered email from the db
	    ###Next will check to see if it exists
	    	##If email exists, check password
	    		##If password is correct, go to logged in page
	    	##Else return error 

	    # email = request.form.get("email")
	    # password = request.form.get("password")
	    # new_email = db.execute("SELECT password FROM user_logins WHERE email = :email",
	    # 	{"email": email, "password": password}).fetchone()
	    # books.append(new_email)

	    
	return render_template("index.html", books=books)

@app.route("/#", methods=["POST"])
def logout():
	session.clear()
	return render_template("index.html", books=books)

@app.route("/register", methods=["GET", "POST"])
def register():
	msg = "Join the Scrolled clan"
	registered = False
	url = 'index'
	if request.method == "POST":
		return_list = get_form_data(request_list)
		
		# username = request.form.get("username")
		db.execute("INSERT INTO user_logins (password, email) VALUES (:password, :email)",
							{"password":return_list[0], "email": return_list[1]})
		db.execute('''INSERT INTO user_details (first_name, last_name, dob, country) 
					  VALUES (:first_name, :last_name, :dob, :country)''',
							{"first_name":return_list[2], "last_name": return_list[3],
					 	    "dob": int(return_list[4]),"country": return_list[5]})
		# db.execute("INSERT INTO user_likes (author, book) VALUES (:author, :book)",
		# 					{"author":return_list[6], "book": return_list[7]})
		#if dob != None:
		db.commit()
		msg = "Registration Successful"
		registered = True
		url = 'home'
			# retrieved_id = db.execute("SELECT user_id FROM user_logins WHERE email = :email",
			# 	{"email": return_list[1]}).fetchone()
			# db.execute('''INSERT INTO user_details (user_id) 
			# 	VALUES (:user_id)'''), {"user_id":retrieved_id }
			# db.commit()
		# except exc.SQLAlchemyError:
		# 	msg = "Email already registered... "
		# 	registered = False
	return render_template("register.html", msg=msg, registered=registered, url=url)

	

@app.route("/home", methods=["GET"])
def home():
	# rows = db.execute("""SELECT book, author FROM user_likes JOIN user_logins
	# 	ON user_logins.user_id = user_likes.user_id 
	# 	WHERE user_likes.user_id = :user_id""", {"user_id": session["user_id"]}).fetchall()

	rows = db.execute("""SELECT book, author FROM user_likes  
		WHERE user_id = :user_id""", {"user_id":session["user_id"]}).fetchall()

	deets = db.execute("""SELECT first_name FROM user_details 
		WHERE details_id = :user_id""", {"user_id":session["user_id"]}).fetchone()

	return render_template("home.html", rows=rows, name=deets.first_name)

@app.route("/about", methods=["GET"])
def about():
	return render_template("about.html")
	
@app.route("/about", methods=["POST"])
def update_about():
	get_form_data(request_list)
	db.execute("INSERT INTO user_likes (author, book, user_id) VALUES (:author, :book, :user_id)",
							{"author":return_list[6], "book": return_list[7], "user_id":session["user_id"]})
	db.commit()
	return render_template("about.html")	


@app.route("/", methods=["POST"])
def login():
	email = request.form.get("email")
	password = request.form.get("password")
	##not sure what this logins thing is supposed to be for below... can't remeber why i did it...
	logins = db.execute("SELECT * FROM user_logins WHERE email = :email and password = :password",
	    {"email": email, "password": password}).fetchone()
	##try and log into user, load name up on next page if successful, reload page with error if not
	try:
		usr_name = db.execute("""SELECT * FROM user_details JOIN user_logins
				ON user_logins.user_id = user_details.details_id
				WHERE email = :email """, {"email":email}).fetchone() 
		session["user_id"] = usr_name.user_id
		return home()
		#return render_template("home.html", name=usr_name.first_name)	
	except:
		return render_template("index.html", fail=fail)

@app.route("/home", methods=["GET", "POST"])
def search():
	avg_rating = 0
	counter = 0
	try:
		entry = request.form.get("search")
		rows = db.execute("SELECT * FROM books WHERE book_name = :search or author =:search",
			{"search":entry}).fetchall()

		book_id = rows[0]["book_id"]
		#reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id  and reviewer_id = :reviewer_id", {"book_id":book_id, "reviewer_id":session["user_id"]}).fetchall()
		# for e in reviews:
		# 	avg_rating += int(reviews[0]["rating"])
		# 	counter += 1
		# if avg_rating > 0:
		# 	avg_rating = avg_rating / counter
		# else:
		# 	avg_rating == "Not rated"
	except Exception:
		rows=[]
	return render_template("results.html", rows=rows)



@app.route("/results", methods=["POST"])
def get_book():

	row = request.form.get('clicked')
	row = row.split(",")
	book_id = row[0][1:]
	rating = "Not yet rated"
	review = "Not yet reviewed"
	avg_ints = []

	reviews = db.execute('''SELECT * FROM reviews 
		WHERE book_id = :book_id''', 
		{"book_id":book_id}).fetchall()

	avg_rating = db.execute('''SELECT AVG(rating) FROM reviews 
		WHERE book_id = :book_id''', {"book_id":book_id}).fetchone()

	for e in reviews:
		if e.reviewer_id == session["user_id"]:
			rating = e.rating
			review = e.review

	# for x in avg_rating:
	# 	for e in x:
	# 		avg_ints.append(float("{0:.2f}".format(e)))

	session["clicked"] = [row, rating, review, book_id]
	if avg_rating[0] != None:
		avg_rating = "{0:.2f}".format(avg_rating[0])
	else:
		avg_rating = "Not yet rated"


	return render_template("book_page.html", row=session["clicked"][0], 
		rating=session["clicked"][1], avg_rating=avg_rating,
		review=session["clicked"][2])

# might need to use that weird variable URL string that changes according to input that's on cs50 vid
# @app.route("/book_page", methods=["GET", "POST"])
# def book_page():
	
	# review = "You haven't reviewed this yet."
	# rating = "Not yet rated"
	# avg_rating = "Not yet rated"
	# counter = 0
	
	
	
	# # only change value if clicked, else see 'except'
	# row = request.form.get('clicked')
	# if row != None:
	# 	row = row.split(",")
	# 	session["clicked"] = row
	# 	book_id = row[0][1:]
	# else:
	# 	print("not clicked")
	# 	book_id = session["clicked"][3]
	# 	row = session["clicked"][0]
	# avg_rating = 0

	# print("working")
	# # reviews = db.execute('''SELECT rating, review FROM reviews 
	# # 	WHERE book_id = :book_id  and reviewer_id = :reviewer_id''', 
	# # 	{"book_id":book_id, "reviewer_id":session["user_id"]}).fetchone()
	# reviews = db.execute('''SELECT * FROM reviews 
	# 	WHERE book_id = :book_id''', 
	# 	{"book_id":book_id}).fetchall()

	# for e in reviews:
	# 	if e.reviewer_id == session["user_id"]:
	# 		rating = e.rating
	# 		review = e.review

	# if reviews == None:
	# 	pass
	# else:
	# 	for e in reviews:
	# 		avg_rating += int(e["rating"])
	# 		counter += 1
	# if avg_rating > 0:
	# 	avg_rating = avg_rating / counter
	# 	avg_rating = "{0:.2f}".format(avg_rating)
	# else:
	# 	avg_rating = "Not rated"
	
	# # session["clicked"] = [row, reviews]
	# session["clicked"] = [row, rating, review, book_id]

	# # if not clicked on, then the radio form must have been submitted
	# #rate()
		
	
	

	# #id_for_reviews = row[0] # This is a test for how to access reviews when needed
	# #print("row: ", row)
	# # return render_template("book_page.html", row=session["clicked"][0], rating=reviews.rating, review=reviews.review)
	# return render_template("book_page.html", row=session["clicked"][0], 
	# 	rating=session["clicked"][1], avg_rating=avg_rating,
	# 	review=session["clicked"][2])

@app.route("/book_page", methods=["POST"])
def rate():
	# only do the following if form submitted, not simple page reload
	if request.method == "POST":
		#try:
		print("This part")
		rating = int(request.form.get("usr_rating"))
		review = request.form.get("texty")
		print("rating: ", rating)
		print("review: ", review)
		book_id = int(session["clicked"][0][0][1:])

		# Delete old review and replace with new one. Deletes old review and rating.
		#TODO: Prabably should make 'submit review' a sperate form so user can submit one without effectng the other
		db.execute("DELETE FROM reviews WHERE book_id = :book_id and reviewer_id = :reviewer_id", {"book_id":book_id, "reviewer_id":session["user_id"]})
		db.execute("INSERT INTO reviews (book_id, rating, review, reviewer_id) VALUES (:book_id, :rating, :review, :reviewer_id)", 
			{"book_id":book_id, "rating":rating, "review": review, "reviewer_id":session["user_id"]})
		db.commit()
		avg_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :book_id", {"book_id":book_id}).fetchone()
		avg_rating = "{0:.2f}".format(avg_rating[0])
		#except Exception:
			#print("error")
		return render_template("book_page.html", row=session["clicked"][0], 
		rating=rating, avg_rating=avg_rating,
		review=review)
			

# TODO:
# 1: add new table:
		#reviews_table
		#review_id, book_id, rating, review
# 2: new book page:
		#page that displays info about book:
		# - shows same info as before but one page

# 3: look into api stuff
