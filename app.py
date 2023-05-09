import sys
import sqlite3 as sql3
from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash,check_password_hash

# Configure app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setup to use SQLite database
con = sql3.connect("movie-recommendation.db", check_same_thread=False)
cur = con.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


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

        # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        print("fetchall(): ", fetchall(), file=sys.stdout)
        print("fetchone(): ", fetchone(), file=sys.stdout)
        if len(rows.fetchall()) == 1:
            if check_password_hash(rows.fetchone()["hash"], (password,)):

                # Password correct
                user_id = rows.fetchone()["id"]
                session["user_id"] = user_id
                return redirect("/")

            else:
                # Password Incorrect
                flash("Password incorrect")
                return render_template("login.html", 'error')

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

        # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = ?", (username,))

        if len(rows) > 0:
            # Username already exists
            flash("This username already exists", 'error')
            return redirect("/register")

        else:
            # Registered successfully
            hash = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username,), (hash,))
            flash("User has been registered successfully!")
            user_id = cur.execute("SELECT id FROM users WHERE username = ?", (username,))[0]["id"]
            session["user_id"] = user_id
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/search")
def search():
    q = request.args.get("q")
    if q:
        shows = {}
        if cur.execute("SELECT EXISTS (SELECT 1 FROM people WHERE name LIKE ?) AS person_exist", '%' + q + '%')[0]['person_exist'] == 1:
            shows['stars'] = cur.execute("SELECT id,title FROM movies m INNER JOIN ratings r ON r.movie_id = m.id WHERE id IN (SELECT movie_id FROM stars s INNER JOIN people p ON p.id = s.person_id AND p.name LIKE ?) ORDER BY rating DESC LIMIT 5", '%' + q + '%')

        if cur.execute("SELECT EXISTS (SELECT 1 FROM movies WHERE title LIKE ?) AS movie_exist", '%' + q + '%')[0]['movie_exist'] == 1:
            shows['movies'] = cur.execute("SELECT id,title FROM movies m INNER JOIN ratings r ON r.movie_id = m.id WHERE title LIKE ? ORDER BY rating DESC LIMIT 5", '%' + q + '%')

    else:
        shows = {}
    return jsonify(shows)


@app.route("/like")
def like():
    user_id = session['user_id']
    if request.method == "POST":
        if not request.form.get("id"):
            status = "no movie_id"
        else:
            movie_id = request.form.get("id")
            if cur.execute("SELECT EXISTS (SELECT 1 FROM likes WHERE user_id = ? AND movie_id = ?)", (user_id,), (movie_id,)):
                cur.execute("DELETE FROM likes WHERE user_id = ? AND movie_id = ?", (user_id,), (movie_id,))
                status = "unliked"
            else:
                cur.execute("INSERT INTO likes (user_id, movie_id) VALUES(?, ?)", (user_id,), (movie_id,))
                status = "liked"
        return jsonify(status)
    else:
        print("Not POST method")
        return jsonify(status)