import sys
import os
import sqlalchemy
from sql_helpers import getconn
from werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
import json
import threading
import pandas as pd
import numpy as np
from sklearn.metrics import jaccard_score
import redis
from config import SECRET_KEY

# Configure app
app = Flask(__name__)
current_query_lock = threading.Lock() # Lock for current_query
cancel_flag = False # Flag to cancel current query

# Configure redis
redis_host = os.environ.get('REDISHOST', 'localhost')
redis_port = int(os.environ.get('REDISPORT', 6379))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Create a secret key
app.secret_key = SECRET_KEY

# Configure session
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(host=redis_host, port=redis_port)
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
        return render_template("index.html", username=session["user_name"])


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
                    session["user_name"] = username
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
    # Set cancellation flag and acquire the lock
    global cancel_flag
    cancel_flag = False
    current_query_lock.acquire()

    try:
        if cancel_flag:
            return jsonify({'message': 'Query canceled'})   
        q = request.args.get("q")
        if q:
            with pool.connect() as db_conn:

                data = {'titles': {}, 'names': {}}
                
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
                    SELECT tb.id as titleId, tb.primaryTitle, tb.titleType, averageRating, startYear, genres, l.userId IS NOT NULL AS liked
                    FROM title_basics tb 
                    INNER JOIN title_rating tr ON tr.titleId = tb.id
                    INNER JOIN title_principals tp ON tp.titleId = tb.id
                    LEFT JOIN likes l ON tb.id = l.itemId
                    AND l.userId = :userId
                    WHERE primaryTitle LIKE :primaryTitle
                    ORDER BY tr.averageRating DESC LIMIT 10
                    """)
                    
                    rows = db_conn.execute(create_txt, {"primaryTitle": q, "userId": session['user_id']}).fetchall()
                    for row in rows:
                        if cancel_flag:
                            return jsonify({'message': 'Query canceled'})
                        
                        data['titles'][row.titleId] = dict({"primaryTitle":row.primaryTitle, "titleType":row.titleType, "averageRating":row.averageRating, "startYear":row.startYear, "genres":row.genres, "liked":row.liked})
                    
                    print("Stored data in data['titles']")

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
                    SELECT nb.id as personId, nb.primaryName, birthYear, deathYear, primaryProfession, knownForTitles, l.userId IS NOT NULL AS liked
                    FROM name_basics nb
                    LEFT JOIN likes l ON nb.id = l.itemId
                    AND l.userId = :userId
                    WHERE nb.primaryName LIKE :primaryName
                    ORDER BY nb.primaryName DESC LIMIT 10
                    """)
                    
                    rows = db_conn.execute(create_txt, {"userId": session["user_id"], "primaryName": q}).fetchall()
                    
                    for row in rows:
                        if cancel_flag:
                            return jsonify({'message': 'Query canceled'})

                        # Get Primary Title for "knownForTitles" column
                        if row.knownForTitles:

                            # Split knownForTitles into list, striping '\r' of the last element
                            knownForTitles = row.knownForTitles.strip('\r').split(',')
                            newKnownForTitles = [f'{title}' for title in knownForTitles]

                            # Create string of knownForTitles to use in SQL query, adding quotes otherwise SQL will not recognize it as a string
                            newKnownForTitles = "', '".join(newKnownForTitles)
                            newKnownForTitles = "'" + newKnownForTitles + "'"

                            # Query database for primaryTitle
                            create_txt = sqlalchemy.text(f"SELECT primaryTitle FROM title_basics WHERE id IN ({newKnownForTitles})")
                            result = db_conn.execute(create_txt).fetchall()                            
                            primaryTitles = [row[0] for row in result]
                            primaryTilesString = ', '.join(primaryTitles)
                        else:
                            primaryTilesString = None
                                                
                        data["names"][row.personId] = dict({"primaryName":row.primaryName, "birthYear": row.birthYear, "deathYear":row.deathYear, "primaryProfession": row.primaryProfession, "knownFor": primaryTilesString, "liked":row.liked})

                    print("Stored data in data['names']")

                else:
                    print("No person found")

        else:
            data = {}
    
    finally:
        # Release the lock
        current_query_lock.release()

    return jsonify(data)


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


@app.route("/recommend_collab", methods=["GET"])
def recommend_collab():
    # Check if user is logged in
    if session["user_id"] == None:
        return redirect("/login")

    target = session["user_id"]

    # Connect to database
    with pool.connect() as db_conn:

        # Get liking data from database
        create_txt = sqlalchemy.text("""
            SELECT userId, itemId
            FROM likes
            LIMIT 100
            """)
        print("Retrieving liking data...")
        rows = db_conn.execute(create_txt).fetchall()
        print("rows: ", rows)
        
        itemIds = np.empty(0)
        userIds = np.empty(0)

        for row in rows:
            itemIds = np.append(itemIds, row.itemId)
            userIds = np.append(userIds, row.userId)
        print("itemIds: ", itemIds)
        print("userIds: ", userIds)

        df = pd.DataFrame({"userId": userIds, "itemId": itemIds})
        print("df: ", df)

        # Get unique userIds and itemIds
        unique_itemIds = np.unique(itemIds)
        print("unique_itemIds: ", unique_itemIds)
        unique_userIds = np.unique(userIds)
        print("unique_itemIds: ", unique_itemIds)

        # Get unique itemIds liked by target user
        unique_itemIds_target = df.loc[df.userId == target]
        print("unique_itemIds_target: ", unique_itemIds_target)
        unique_itemIds_target = sorted(set(unique_itemIds_target.itemId))
        print("unique_itemIds_target: ", unique_itemIds_target)

        # Get unique userIds who liked the same items as target user
        unique_userIds_except_target = unique_userIds
        print("unique_userIds_except_target: ", unique_userIds_except_target)
        
        # Delete target user from the list
        for i in range(len(unique_userIds_except_target)):
            if unique_userIds_except_target[i] == target:
                unique_userIds_except_target = np.delete(unique_userIds_except_target, i)
                break
        print("Deleted target user from the list")
                
        #unique_userIds_except_target.remove(target)
        print("unique_userIds_except_target: ", unique_userIds_except_target)

        jaccard_score_list = {'userId': [], 'jaccard_score': []}
        for user in unique_userIds_except_target:
            other_user_liking = np.empty(len(unique_itemIds_target))
            target_user_liking = np.full(len(unique_itemIds_target), 1)
            for i, item in enumerate(unique_itemIds_target):

                # Populate binary liking values for the collaborator
                print("Populating binary liking values for the collaborator")
                if df.loc[(df.userId == user) & (df.itemId == item)].empty:
                    other_user_liking[i] = 0
                else:
                    other_user_liking[i] = 1

            # Calculate Jaccard score
            print("Calculating Jaccard score")
            jaccard_score_list['userId'].append(user)
            jaccard_score_list['jaccard_score'].append(jaccard_score(target_user_liking, other_user_liking))

        # Sort the list by Jaccard score
        print("Sorting the list by Jaccard score")
        df_jaccard_score = pd.DataFrame(jaccard_score_list)
        df_jaccard_score = df_jaccard_score.sort_values(by=['jaccard_score'], ascending=False)
        print("df_jaccard_score: ", df_jaccard_score)

        collab = df_jaccard_score.loc[df_jaccard_score.jaccard_score == df_jaccard_score.jaccard_score.max()].userId.values[0]
        print("collab: ", collab)

        print("df: ", df)
        collab_likes = df.loc[df.userId == collab].itemId
        print("collab_likes: ", collab_likes)

        # Remove items already liked by target user
        print("Removing items already liked by target user")
        recommendation = collab_likes[~collab_likes.isin(unique_itemIds_target)]
        print("recommendation: ", recommendation)

        # Get the top 10 items(if available)
        print("Getting the top 10 items(if available)")
        if len(recommendation) > 10:
            recommendation = recommendation[:10]
        else:
            recommendation = recommendation[:len(recommendation)]

        # Get the title of the items
        reco_collab = {"titles":[], "persons":[]}
        print("Getting items")
        for item in recommendation:
            print("item: ", item)
            if item[0] == "t":
                create_txt = sqlalchemy.text("""
                    SELECT primaryTitle, id
                    FROM title_basics
                    WHERE id = :item
                    """)
                print("Retrieving recommended items...")
                result = db_conn.execute(create_txt, {"item": item}).fetchone()
                print("result: ", result)
                reco_collab['titles'].append(dict({"itemId":result.id, "primaryTitle":result.primaryTitle}))
            elif item[0] == "n":
                create_txt = sqlalchemy.text("""
                    SELECT primaryName, id
                    FROM name_basics
                    WHERE id = :item
                    """)
                print("Retrieving recommended items...")
                result = db_conn.execute(create_txt, {"item": item}).fetchone()
                print("result: ", result)
                reco_collab['persons'].append(dict({"itemId":result.id, "primaryName":result.primaryName}))

            else:
                print("Error: item is neither title nor person")

        return render_template("recommend_collab.html", reco_collab=reco_collab)