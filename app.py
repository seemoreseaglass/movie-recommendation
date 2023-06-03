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
        with pool.connect() as db_conn:
            slct_user = sqlalchemy.text("SELECT username FROM users WHERE id = :id")
            username = db_conn.execute(slct_user, {"id":session["user_id"]}).fetchall()[0][0]
        return render_template("index.html", username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

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
            result = db_conn.execute(create_txt, {"primaryTitle": q}).fetchall()

            if result[0][0] == 1:
                create_txt = sqlalchemy.text("""
                SELECT id, primaryTitle FROM title_basics tb 
                INNER JOIN title_rating tr ON tr.titleId = tb.id
                WHERE primaryTitle LIKE :primaryTitle
                ORDER BY tr.averageRating DESC LIMIT 5
                """)
                rows = db_conn.execute(create_txt, {"primaryTitle": q}).fetchall()
                shows['titles'] = [{"titleId":row.id, "primaryTitle":row.primaryTitle} for row in rows]

                # Check if titleId and userId exists in likes table 
                for show in shows['titles']:
                    create_txt = sqlalchemy.text("""
                    SELECT EXISTS (SELECT 1 FROM likes WHERE titleId = :titleId AND userId = :userId) AS liked
                    """)
                    result = db_conn.execute(create_txt, {"titleId": show['titleId'], "userId": session["user_id"]}).fetchall()

                    if result[0][0] == 1:
                        show['liked'] = True

                    else:
                        show['liked'] = False

            else:
                print("No movie found")
            
            # Query database by names
            create_txt = sqlalchemy.text("""
                SELECT EXISTS (SELECT 1 FROM name_basics WHERE primaryName LIKE :primaryName) AS person_exist
            """)
            result = db_conn.execute(create_txt, {"primaryName": q}).fetchall()

            if result[0][0] == 1:
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

                # Check if titleId and userId exists in likes table
                for show in shows["names"]:
                    print(show)
                    create_txt = sqlalchemy.text("""
                    SELECT EXISTS (SELECT 1 FROM likes WHERE titleId = :titleId AND userId = :userId) AS liked
                    """)
                    result = db_conn.execute(create_txt, {"titleId": show["titleId"], "userId": session["user_id"]}).fetchall()

                    if result[0][0] == 1:
                        show["liked"] = True

                    else:
                        show["liked"] = False

            else:
                print("No person found")

    else:
        shows = {}
    print("Number of titles: ", len(shows["titles"]))
    print("Number of names: ", len(shows["names"]))
    return jsonify(shows)


@app.route("/like")
def like():
    # Get data from request
    data = json.loads(request.data)
    userId = session["user_id"]
    titleId = data.get("titleId")
    action = data.get("action")
    
    # Check if title_id and action are provided
    if not title_id or not action:
        return jsonify({"error": "Invalid request"})
    
    # Check if the user already liked the title
    create_txt = sqlalchemy.text("""
        SELECT EXISTS (SELECT 1 FROM likes WHERE user_id = :userId AND titleId = :titleId)
        """)
    
    result = db_conn.execute(create_txt, {"userId": userId, "titleId": titleId}).fetchall()
    print("result: ", result)
    if action == "like":
        if result[0][0] == 1:
            return jsonify({"error": "Already liked"})
        else:
            create_txt = sqlalchemy.text("""
                INSERT INTO likes (userId, titleId) VALUES (:userId, :titleId)
                """)
            db_conn.execute(create_txt, {"userId": userId, "titleId": titleId})
            db_conn.commit()
            return jsonify({"status": "Liked"})
    elif action == "unlike":
        if result[0][0] == 0:
            return jsonify({"error": "You haven't liked this title"})
        else:
            create_txt = sqlalchemy.text("""
                DELETE FROM likes WHERE userId = :userId AND titleId = :titleId
                """)
            db_conn.execute(create_txt, {"userId": userId, "titleId": titleId})
            db_conn.commit()
            return jsonify({"status": "Unliked"})
    else:
        return jsonify({"error": "Invalid action"})