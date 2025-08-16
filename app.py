import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd, membership_required
from random import SystemRandom
import string

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Remove SERVER_NAME for production deployment
# app.config["SERVER_NAME"] = "teampostapp.local"
app.secret_key = os.environ.get("SECRET_KEY", "Supersecretkey")
Session(app)


# Configure CS50 Library to use SQLite database
# Use absolute path for database in production
database_path = os.path.join(os.path.dirname(__file__), "teampost.db")
db = SQL(f"sqlite:///{database_path}")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    next_url = request.args.get("next")
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        next_url = request.form.get("next_url")
        if not next_url:
            next_url = "/"
        print(next_url)
        return redirect(next_url)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("missing username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("missing password", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords don't match", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username isn't taken
        if len(rows) != 0:
            return apology("username taken", 400)

        user_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
                "username"), generate_password_hash(password=request.form.get("password"))
        )

        # Remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """ Get account information """

    # Get user's id
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get the form's inputs
        new_username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        current_password = request.form.get("current_password")

        # Validate current password
        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], current_password):
            return apology("invalid password", 403)

        # If user wants to change username
        if new_username:
            # Check if username is taken
            existing_user = db.execute("SELECT * FROM users WHERE username = ?", new_username)
            if existing_user:
                return apology("username taken", 400)

            # Update username
            db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, user_id)

        # If user wants to change password
        if new_password:
            # Check if the user confirmed their password
            if not confirmation:
                return apology("confirm new password", 400)
            if new_password != confirmation:
                return apology("new passwords do not match", 400)

            # Update password
            new_hash = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, user_id)

        flash("Changes saved!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("account.html")


@app.route("/explore", methods=["GET", "POST"])
def explore_teams():
    teams = db.execute("""
        SELECT teams.id, teams.name, teams.description, COUNT(team_members.user_id) AS member_count
        FROM teams
        LEFT JOIN team_members
            ON teams.id = team_members.team_id
        WHERE teams.access_type = 'public'
        AND teams.id NOT IN (
            SELECT team_id
            FROM team_members
            WHERE user_id = ?
        )
        GROUP BY teams.id
        ORDER BY member_count DESC
        """, session["user_id"])

    if request.method == "POST":
        team_id = request.form.get("team_id")
        selected_team = next((team for team in teams if str(team["id"]) == team_id), None)
        if selected_team:
            db.execute("""
                INSERT INTO 
                team_members (team_id, user_id, privilege) 
                VALUES (?, ?, 'read')
                """, team_id, session["user_id"])
            flash(f"You have successfully joined {selected_team["name"]} ")
        else:
            flash("Invalid team ID")
        return redirect("/explore")

    else:
        print(teams)
        return render_template("explore.html", teams=teams)
   
   
   
@app.route("/teams", methods=["GET"])
@login_required
def view_teams():
    teams = db.execute("""
        SELECT teams.id, teams.name, teams.description, team_members.privilege, COUNT(team_members.user_id) AS member_count
        FROM teams
        LEFT JOIN team_members
            ON teams.id = team_members.team_id
        WHERE team_members.user_id = ?
        GROUP BY teams.id
        ORDER BY team_members.privilege
        """, session["user_id"])

    return render_template("teams.html", teams=teams)



@app.route("/team/<int:team_id>")
@membership_required
def team_page(team_id):

    topics = db.execute("""
        SELECT topics.id, topics.name, team_topics.team_id
        FROM topics 
        JOIN team_topics ON topics.id = team_topics.topic_id
        WHERE team_topics.team_id = ?
        ORDER BY topics.name
    """, team_id)

    return render_template("team_page.html", topics=topics)


@app.route("/team/<int:team_id>/topic/<string:topic_name>")
@membership_required
def board(team_id, topic_name):
    statuses = [
        {"id": "todo", "name": "To Do"},
        {"id": "doing", "name": "Doing"},
        {"id": "done", "name": "Done"},
        {"id": "delete", "name": "DELETE"}
    ]

    cards = db.execute("""
        SELECT notes.id, notes.content, notes.status, topic_notes.topic_id
        FROM notes
        JOIN topic_notes ON notes.id = topic_notes.note_id
        JOIN team_topics ON topic_notes.topic_id = team_topics.topic_id
        JOIN topics ON team_topics.topic_id = topics.id
        WHERE team_topics.team_id = ?
        AND topics.name = ?
    """, team_id, topic_name.capitalize())

    return render_template("board.html", statuses=statuses, cards=cards)


@app.route("/move_note", methods=["POST"])
@membership_required
def move_note():
    data = request.get_json()
    note_id = data["note_id"]
    new_status = data["column_id"]

    if new_status == "delete":
        db.execute("DELETE FROM notes WHERE id = ?", note_id)
    else:
        db.execute("UPDATE notes SET status = ? WHERE id = ?", new_status, note_id)

    return jsonify({"status": "success"})

@app.route("/create_team", methods=["GET", "POST"])
@login_required
def create_team():
    if request.method == "GET":
        teams = db.execute("""
            SELECT teams.id, teams.name, teams.description, team_members.privilege, COUNT(team_members.user_id) AS member_count
            FROM teams
            LEFT JOIN team_members
                ON teams.id = team_members.team_id
            WHERE team_members.user_id = ?
            GROUP BY teams.id
            ORDER BY team_members.privilege
            """, session["user_id"])
        return render_template("teams.html", teams= teams, method="get")
    
    else:
        team_name = request.form.get("team-name")
        team_code = request.form.get("team-code")
        team_description = request.form.get("team-description")
        team_access_type = request.form.get("team-access-type")

        for field_name, field_value in [("team name", team_name), ("team status", team_access_type)]:
            if field_value is None or field_value.strip() == "":
                return render_template("error.html", error=f"Missing {field_name} for team creation!")
        
        print(team_code)
        if team_code == "":
            team_code = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
        print(team_code)
        
        if len(team_name) > 30:
            return render_template("error.html", error=f"Team name contains {len(team_name)} characters, limit is 30!")
        
        if len(team_name) < 7:
            return render_template("error.html", error=f"Team name contains {len(team_name)} characters, must be at least 7 characters long!")

        taken = db.execute("SELECT 1 FROM teams WHERE name = ?", team_name)

        if taken:
            return render_template("error.html", error="Desired name is already taken!")
        
        if len(team_code) > 12:
            return render_template("error.html", error=f"Team code contains {len(team_code)} characters, limit is 12!")

        if team_access_type not in ("public", "private"):
            return render_template("error.html", error="Invalid team status")
        db.execute("INSERT INTO teams (name, code, description, access_type) VALUES (?, ?, ?, ?)", team_name, team_code, team_description, team_access_type)
        new_team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)[0]["id"]
        db.execute("INSERT INTO team_members (team_id, user_id, privilege) VALUES (?, ?, ?)", new_team_id, session["user_id"], "admin")
        flash(f"Successfully created {team_name}!")
        return redirect("/teams")


@app.route("/check_name", methods=["POST"])
@login_required
def check_name():
    name = request.get_json()
    team_name = name.get("name")
    if not team_name:
        return jsonify({
            "success": False,
            "error": "Team name can't be blank"
        })

    taken = db.execute("SELECT 1 FROM teams WHERE name = ?", team_name)

    if taken:
        return jsonify({
            "success": False,
            "error": "Desired name is already taken!"
        })

    team_name_length = len(team_name)
    if team_name_length > 30:
        return jsonify({
            "success": False,
            "error": f"Team name contains {team_name_length} characters, limit is 30!"
        })

    if team_name_length < 7:
        return jsonify({
            "success": False,
            "error": f"Team name contains {team_name_length} characters, must be at least 7 characters long!"
        })

    else:
        return jsonify({"success": True})


@app.route("/check_code", methods=["POST"])
def check_code():
    data = request.get_json()
    team_code = data.get("code")

    team_code_length = len(team_code)
    if team_code_length > 12:
        return jsonify({
            "success": False,
            "error": f"Team code contains {team_code_length} characters, limit is 12!"
        })

    if team_code_length < 6:
        return jsonify({
            "success": False,
            "error": f"Team code contains {team_code_length} characters, must be at least 6 characters long!"
        })

    else:
        return jsonify({"success": True})


@app.route("/leave_team", methods=["POST"])
@login_required
def leave_team():
    data = request.get_json()
    print(data)
    team_id = data.get("team_id")
    left_team_count = db.execute("DELETE FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])
    if left_team_count == 0:
        return jsonify({"success": False})    
    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

