import sys
import sqlalchemy
from sql_helpers import getconn
from werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
import json

# Configure app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Create connection pool
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if session.get("user_id") is None:
        return redirect("/login")
    else:
        """
        Delete this later
        """
        return render_template("index.html", username='test')
        """
        Delete this later
        """
        with pool.connect() as db_conn:
            slct_user = sqlalchemy.text("SELECT username FROM users WHERE id = :id")
            username = db_conn.execute(slct_user, {"id":session["user_id"]}).fetchall()[0][0]
        return render_template("index.html", username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    """
    Delete this later
    """
    session["user_id"] = 9
    return redirect("/")
    """
    Delete this later
    """
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", 'error')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", 'error')
            return render_template("login.html")

        username = request.form.get("username")
        password = request.form.get("password")

        with pool.connect() as db_conn:
            
            # Query database for username
            slct_lgin = sqlalchemy.text("SELECT * FROM users WHERE username = :username") 
            rows = db_conn.execute(slct_lgin, {"username":username}).fetchall()
            if len(rows) == 1:
                if check_password_hash(rows[0][2], password):

                    # Password correct
                    user_id = rows[0][0]
                    session["user_id"] = user_id
                    return redirect("/")

                else:
                    # Password Incorrect
                    flash("Password incorrect", 'error')
                    return render_template("login.html")

  
            else:
                flash("username doesn't exist", 'error')
                return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", 'error')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", 'error')
            return render_template("login.html")

        username = request.form.get("username")
        password = request.form.get("password")

        # Check if username already exists
        with pool.connect() as db_conn:

            # Query database for username
            slct_register = sqlalchemy.text("SELECT * FROM users WHERE username = :username")
            rows = db_conn.execute(slct_register, {"username":username}).fetchall()

            if len(rows) > 0:
                # Username already exists
                flash("This username already exists", 'error')
                return redirect("/register")

            else:
                # Register new user
                hash = generate_password_hash(password)
                inst_register = sqlalchemy.text("INSERT INTO users (username, hash) VALUES(:username, :hash)")
                db_conn.execute(inst_register, {"username":username, "hash":hash})
                
                # commit transaction
                db_conn.commit()
                flash("User has been registered successfully!")
                id_register = sqlalchemy.text("SELECT id FROM users WHERE username = :username")
                user_id = db_conn.execute(id_register, {"username": username}).fetchall()[0][0]
                session["user_id"] = user_id
                return redirect("/")
    else:
        return render_template("register.html")


@app.route("/search")
def search():
    q = request.args.get("q")
    if q:
        with pool.connect() as db_conn:

            shows = {'titles': [], 'names': []}
            
            q = '%' + q + '%'

            # Query database by titles
            create_txt = sqlalchemy.text("""
                SELECT EXISTS (SELECT 1 FROM title_basics WHERE primaryTitle LIKE :primaryTitle) AS movie_exist
            """)
            print("Checking if", q, "exists in title_basics table...")
            result = db_conn.execute(create_txt, {"primaryTitle": q}).fetchall()

            if result[0][0] == 1:
                print("Found", q, "in title_basics table. Retrieving data...")
                create_txt = sqlalchemy.text("""
                SELECT id, primaryTitle FROM title_basics tb 
                INNER JOIN title_rating tr ON tr.titleId = tb.id
                WHERE primaryTitle LIKE :primaryTitle
                ORDER BY tr.averageRating DESC LIMIT 5
                """)
                rows = db_conn.execute(create_txt, {"primaryTitle": q}).fetchall()
                shows['titles'] = [{"titleId":row.id, "primaryTitle":row.primaryTitle} for row in rows]
                print("Stored data in shows['titles']")

                # Check if titleId and userId exists in likes table 
                print("Checking if each titleId and userId exists in likes table...")
                for show in shows['titles']:
                    create_txt = sqlalchemy.text("""
                    SELECT EXISTS (SELECT 1 FROM likes WHERE itemId = :titleId AND userId = :userId) AS liked
                    """)
                    result = db_conn.execute(create_txt, {"titleId": show['titleId'], "userId": session["user_id"]}).fetchall()

                    if result[0][0] == 1:
                        show['liked'] = True

                    else:
                        show['liked'] = False
                print("Stored 'liked' data in shows['titles']")

            else:
                print("No movie found")
            
            # Query database by names
            create_txt = sqlalchemy.text("""
                SELECT EXISTS (SELECT 1 FROM name_basics WHERE primaryName LIKE :primaryName) AS person_exist
            """)
            print("Checking if", q, "exists in name_basics table...")
            result = db_conn.execute(create_txt, {"primaryName": q}).fetchall()

            if result[0][0] == 1:
                print("Found", q, "in name_basics table. Retrieving data...")
                create_txt = sqlalchemy.text("""
                SELECT tb.id as titleId, tb.primaryTitle, nb.id as personId, nb.primaryName
                FROM title_basics tb
                INNER JOIN title_rating tr ON tr.titleId = tb.id
                INNER JOIN title_principals tp ON tp.titleId = tb.id
                INNER JOIN name_basics nb ON nb.id = tp.personId
                AND nb.primaryName LIKE :primaryName
                ORDER BY tr.averageRating DESC LIMIT 5
                """)
                rows = db_conn.execute(create_txt, {"primaryName": q}).fetchall()
                shows["names"] = [{"titleId":row.titleId, "primaryTitle":row.primaryTitle, "personId":row.personId, "primaryName":row.primaryName} for row in rows]
                print("Stored data in shows['names']")

                # Check if titleId and userId exists in likes table
                print("Checking if each titleId and userId exists in likes table...")
                for show in shows["names"]:
                    print(show)
                    create_txt = sqlalchemy.text("""
                    SELECT EXISTS (SELECT 1 FROM likes WHERE itemId = :titleId AND userId = :userId) AS liked
                    """)
                    result = db_conn.execute(create_txt, {"titleId": show["titleId"], "userId": session["user_id"]}).fetchall()

                    if result[0][0] == 1:
                        show["liked"] = True

                    else:
                        show["liked"] = False
                print("Stored 'liked' data in shows['names']")

            else:
                print("No person found")

    else:
        shows = {}

    return jsonify(shows)


@app.route("/like", methods=["POST"])
def like():
    # Check if user is logged in
    if session.get("user_id") is None:
        return redirect("/login")
    
    # Get data from request
    data = json.loads(request.data)
    userId = session["user_id"]
    itemId = data.get("itemId")
    if itemId[0] == "t":
        itemType = "title"
    elif itemId[0] == "n":
        itemType = "name"
    else:
        return jsonify({"error": "Invalid request"})

    action = data.get("action")
    
    # Check if itemId and action are provided
    if not itemId or not action:
        return jsonify({"error": "Invalid request"})
    
    # Connect to database
    with pool.connect() as db_conn:

        # Check if the user already liked the title
        create_txt = sqlalchemy.text("""
            SELECT EXISTS (SELECT 1 FROM likes WHERE userId = :userId AND itemId = :itemId)
            """)
        print("Checking if the user already liked the title...")
        result = db_conn.execute(create_txt, {"userId": userId, "itemId": itemId}).fetchall()
        
        # For liking the title
        if action == "like":

            # If the user has already liked the title, return error
            if result[0][0] == 1:
                print("Already liked")
                return jsonify({"error": "Already liked"})
            
            # Else, add the like to the database (like)
            else:
                create_txt = sqlalchemy.text("""
                    INSERT INTO likes (userId, itemId, type) VALUES (:userId, :itemId, :type)
                    """)
                db_conn.execute(create_txt, {"userId": userId, "itemId": itemId, "type": itemType})
                db_conn.commit()
                print("Added the item to likes table")

                return jsonify({"status": "Liked"})
        
        # For unliking the title
        elif action == "unlike":

            # If the user hasn't liked the title, return error
            if result[0][0] == 0:
                print("You haven't liked this title")
                return jsonify({"error": "You haven't liked this title"})

            # Else, remove the like from the database (unlike)
            else:
                create_txt = sqlalchemy.text("""
                    DELETE FROM likes WHERE userId = :userId AND itemId = :itemId
                    """)
                db_conn.execute(create_txt, {"userId": userId, "itemId": itemId})
                db_conn.commit()
                print("Deleted the item from likes table")
                
                return jsonify({"status": "Unliked"})
        else:
            return jsonify({"error": "Invalid action"})


@app.route("/favorite", methods=["GET"])
def showFav():
    # Check if user is logged in
    if session.get("user_id") is None:
        return redirect("/login")

    # Create a dictionary for storing liked titles and names
    likes = {}

    # Connect to database
    with pool.connect() as db_conn:

        # For retrieving liked titles
        create_txt = sqlalchemy.text("""
            SELECT l.itemId, tb.primaryTitle
            FROM likes l
            INNER JOIN title_basics tb ON tb.id = l.itemId
            WHERE l.userId = :userId AND l.type = "title"
            """)
        print("Retrieving liked items(title)...")
        rows = db_conn.execute(create_txt, {"userId": session["user_id"]}).fetchall()
        likes['titles'] = [{"titleId":row.itemId, "primaryTitle":row.primaryTitle} for row in rows]
        print(likes['titles'])

        # For retrieving liked names
        create_txt = sqlalchemy.text("""
            SELECT l.itemId, nb.primaryName 
            FROM likes l
            INNER JOIN name_basics nb ON nb.id = l.itemId
            WHERE l.userId = :userId AND l.type = "name"
            """)
        print("Retrieving liked items(name)...")
        rows = db_conn.execute(create_txt, {"userId": session["user_id"]}).fetchall()
        likes['names'] = [{"personId":row.itemId, "primaryName":row.primaryName} for row in rows]
        print(likes['names'])

    return render_template("favorite.html", likes=likes)
