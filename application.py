import os

from flask import Flask, session, render_template, request
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy import exc


#TODO:
# Redo all tables, restarting all data so they all begin at the same int (can just delete main ids)
		#this will enable the request in home to work correctly
# If testing success, do the API stuff
# Quick Sass overview (lecture n stuff)
# Quick Boostrap overview
# USe Sass and Boostrap to style page




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
	reg_success = True
	return_list = []
	reg_dict = {}
	color_dict = {}
	for e in request_list:
		temp = request.form.get(e)
		if temp == "":
			reg_dict[e] = ""
			color_dict[e] = 'background-color:#ffd0c4'
			if reg_success == True:
				reg_success = False
		else:
			reg_dict[e] = temp
			return_list.append(temp)
	if reg_success == False:
		return_list = False
	session["temp_reg"] = reg_dict
	session["colors"] = color_dict
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
	msg_2 = "At Scrolled we are scrolled"
	details = ""
	colors = ""

	if request.method == "POST":
		return_list = get_form_data(request_list)
		if return_list == False:
			msg_2 = "Please enter in all details requested"
			details = session["temp_reg"]
			colors = session["colors"]
			session["temp_reg"] = ""
			session["colors"] = ""

		else:
			# username = request.form.get("username")
			db.execute("INSERT INTO user_logins (password, email) VALUES (:password, :email)",
								{"password":return_list[0], "email": return_list[1]})
			db.execute('''INSERT INTO user_details (first_name, last_name, dob, country) 
						  VALUES (:first_name, :last_name, :dob, :country)''',
								{"first_name":return_list[2], "last_name": return_list[3],
						 	    "dob": return_list[4],"country": return_list[5]})
			# db.execute("INSERT INTO user_likes (author, book) VALUES (:author, :book)",
			# 					{"author":return_list[6], "book": return_list[7]})
			#if dob != None:
			db.commit()
			user_id = db.execute("SELECT user_id FROM user_logins WHERE email = :email",
				{"email": return_list[1]}).fetchone()
			
			session["user_id"] = user_id.user_id

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
	return render_template("register.html", msg=msg, msg_2=msg_2, registered=registered, url=url, details=details, color=colors)

			

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
	return_list = get_form_data(request_list)
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
		entry = "%" + entry + "%"
		rows = db.execute("SELECT * FROM books WHERE book_name LIKE :search or author LIKE :search or ISBN LIKE :search",
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

	# reviews = db.execute('''SELECT * FROM reviews 
	# 	WHERE book_id = :book_id''', 
	# 	{"book_id":book_id}).fetchall()

	reviews = db.execute("""SELECT * FROM user_details JOIN reviews
				ON reviews.reviewer_id = user_details.details_id
				WHERE book_id = :book_id """, {"book_id":book_id}).fetchall()
	#rev_name = rev_name

	avg_rating = db.execute('''SELECT AVG(rating) FROM reviews 
		WHERE book_id = :book_id''', {"book_id":book_id}).fetchone()

	for e in reviews:
		if e.reviewer_id == session["user_id"]:
			rating = e.rating
			review = e.review

	#session["clicked"] = [row, rating, review, book_id]

	session["clicked"] = { "row": row,
						   "rating": rating,
						   "review": review,
						   "reviews": reviews,
						   "book_id": book_id }

	if avg_rating[0] != None:
		avg_rating = "{0:.2f}".format(avg_rating[0])
	else:
		avg_rating = "Not yet rated"


	return render_template("book_page.html", row=session["clicked"]["row"], 
		rating=session["clicked"]["rating"], avg_rating=avg_rating,
		review=session["clicked"]["review"], reviews=session["clicked"]["reviews"])



@app.route("/book_page", methods=["POST"])
def rate():

	if request.method == "POST":

		rating = int(request.form.get("usr_rating"))
		review = request.form.get("texty")
		book_id = int(session["clicked"]["book_id"])

		db.execute("DELETE FROM reviews WHERE book_id = :book_id and reviewer_id = :reviewer_id", {"book_id":book_id, "reviewer_id":session["user_id"]})
		db.execute("INSERT INTO reviews (book_id, rating, review, reviewer_id) VALUES (:book_id, :rating, :review, :reviewer_id)", 
			{"book_id":book_id, "rating":rating, "review": review, "reviewer_id":session["user_id"]})
		db.commit()
		avg_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :book_id", {"book_id":book_id}).fetchone()
		avg_rating = "{0:.2f}".format(avg_rating[0])

		return render_template("book_page.html", row=session["clicked"]["row"], 
		rating=rating, avg_rating=avg_rating, reviews=session["clicked"]["reviews"],
		review=review)
			
