from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
import re
import string
import random

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "Supersduperecretkeythatnoonewillguess"
Session(app)


@app.after_request
def after_request(response):
    """
    Ensure responses aren't cached
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Pretty much copy pasted from 
# https://stackoverflow.com/questions/29332056/global-error-handler-for-any-exception
@app.errorhandler(Exception)
def handle_error(error):
    """
    Handle errors via error.html
    """
    
    error = str(error)
    return render_template("error.html", error=error)


""" 
User account logic and route block start for logging in, registering, and changing username or password.
"""

# Logging in, account managing, registering, and logging out
# have been adapted from CS50's finance problem set
@app.route("/login", methods=["GET"])
def login():
    """
    Show the login page
    """
    
    return render_template("login.html")

@app.route("/login_api", methods=["POST"])
def login_api():
    """
    Log user in
    """
    
    # Forget any user_id
    session.clear()

        
    # Get input data
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # Ensure username was submitted
    if not username:
        return jsonify({"success": False, 
                        "error": "Please provide a username!"})

    # Ensure password was submitted
    if not password:
        return jsonify({"success": False, 
                        "error": "Please provide a password!"})

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return jsonify({"success": False, 
                        "error": "Invalid username and/or password!"})

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]
    session["username"] = rows[0]["username"]

    # Return success
    return jsonify({"success": True})



@app.route("/register", methods=["GET"])
def register():    
    """
    Show register page
    """
    
    # Clear any existing session
    session.clear()

    return render_template("register.html")
    
@app.route("/register_api", methods=["POST"])
def register_api():
    """
    Register new user
    """

    # Clear any existing session
    session.clear()
    
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    confirmation = data.get("confirmation")
    
    # Username validation
    if not username:
        return jsonify({"success": False, 
                        "error": "Please provide a username!"})
        
    # Validate username length requirements
    username_length = len(username)
    if username_length > 15:
        return jsonify({"success": False, 
                        "error": f"Username is {username_length} characters, limit is 15!"})
    if username_length < 5:
        return jsonify({"success": False, 
                        "error": f"Username is {username_length} characters, must be at least 5 characters!"})
        
    # Check if username is already taken
    existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
    if existing_user:
        return jsonify({"success": False, 
                        "error": "Username is already taken!"})

    # Password validation
    if not password:
        return jsonify({"success": False, 
                        "error": "Missing password!"})
        
    # Validate password length and pattern requirements
    password_length = len(password)
    pattern = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}"
    
    if password_length > 20:
        return jsonify({"success": False, 
                        "error": f"Password is {password_length} characters, limit is 20!"})
    if password_length < 8:
        return jsonify({"success": False, 
                        "error": f"Password is {password_length} characters, must be at least 8 characters!"})
    if not re.match(pattern, password):
        return jsonify({"success": False, 
                        "error": "Password must contain at least one number, one uppercase letter, and one lowercase letter!"})
        
    # Check password confirmation
    if not confirmation:
        return jsonify({"success": False, 
                        "error": "Missing password confirmation!"})
    if confirmation != password:
        return jsonify({"success": False, 
                        "error": "Passwords don't match!"})

    # Create user account
    user_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

    if user_id:
        # Log in the new user
        session["user_id"] = user_id
        session["username"] = username

        # Return success response
        return jsonify({"success": True})
    return jsonify({"success": False, 
                    "error": "An error occurred, please try again!"})

@app.route("/account", methods=["GET"])
@login_required
def account():
    """
    Show the account page
    """
    
    return render_template("account.html")
    
@app.route("/account_api", methods=["POST"])
@api_login_required
def account_api():
    """
    Allow user to change account password and username
    """
    
    user_id = session["user_id"]
    data = request.get_json()
    new_username = data.get("username")
    new_password = data.get("new_password")
    confirmation = data.get("confirmation")
    current_password = data.get("current_password")
    
    # Validate current password
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], current_password):
        return jsonify({"success": False, 
                        "error": "Your current password is incorrect, please try again!"})
    
    # Check if any changes are requested
    has_changes = False
    
    # Username validation
    username_valid = True
    if new_username and new_username.strip():
        has_changes = True
        
        # Validate username length requirements
        username_length = len(new_username)
        if username_length > 15:
            return jsonify({"success": False, 
                            "error": f"Username is {username_length} characters, limit is 15!"})
        if username_length < 5:
            return jsonify({"success": False, 
                            "error": f"Username is {username_length} characters, must be at least 5 characters!"})
            
        # Check if username is taken (excluding current user's username)
        current_username = session.get("username")
        if new_username != current_username:
            existing_user = db.execute("SELECT * FROM users WHERE username = ?", new_username)
            if existing_user:
                return jsonify({"success": False, 
                                "error": "Username is already taken!"})
    
    # Password validation
    password_valid = True
    if new_password and new_password.strip():
        has_changes = True
        
        # Validate password length and pattern requirements
        password_length = len(new_password)
        pattern = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}"
        
        if password_length > 20:
            return jsonify({"success": False, 
                            "error": f"Password is {password_length} characters, limit is 20!"})
        if password_length < 8:
            return jsonify({"success": False, 
                            "error": f"Password is {password_length} characters, must be at least 8 characters!"})
        if not re.match(pattern, new_password):
            return jsonify({"success": False, 
                            "error": "Password must contain at least one number, one uppercase letter, and one lowercase letter!"})

        # Check password confirmation
        if not confirmation or confirmation.strip() == "":
            return jsonify({"success": False, 
                            "error": "Please confirm your new password!"})
        if new_password != confirmation:
            return jsonify({"success": False, 
                            "error": "New passwords do not match!"})

    # Check if any changes were requested
    if not has_changes:
        return jsonify({"success": False, 
                        "error": "No changes were made. Please enter a new username or password!"})
    
    # All validations passed - apply changes
    if new_username and new_username.strip() and username_valid:
        db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, user_id)
        success = session["username"] = new_username
    
    if new_password and new_password.strip() and password_valid:
        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, user_id)
    
    flash("Successfully updated your account!")
    return jsonify({"success": True})


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    Log user out
    """

    # Forget any user id
    session.clear()

    # Redirect user to the index page
    flash("Successfully logged out!")
    return redirect("/")

""" 
User account logic and route block end for logging in, registering, and changing username or password.
"""



"""
Logic and route block start regarding team viewing, team creation, team leaving, and team management.
"""
@app.route("/explore", methods=["GET"])
@login_required
def explore():
    """
    Allow user to explore public teams and join them
    """
    
    # Check if user has searched a specific name
    search_query = request.args.get("search", "")

    if search_query:
        teams = db.execute("""
            SELECT id, name, description, access_type, code,
            (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
            FROM teams
            WHERE teams.id NOT IN 
            (SELECT team_id FROM team_members WHERE user_id = ?)
            AND access_type != 'private'
            AND teams.name LIKE ?
            ORDER BY teams.name ASC
            """, session["user_id"], f"%{search_query}%")

    else:
        teams = db.execute("""
            SELECT id, name, description, access_type, code,
            (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
            FROM teams
            WHERE teams.id NOT IN 
            (SELECT team_id FROM team_members WHERE user_id = ?)
            AND access_type != 'private'
            ORDER BY teams.name ASC
            """, session["user_id"])
        
    return render_template("explore.html", teams=teams)

@app.route("/join_team_api", methods=["POST"])
@api_login_required
def join_team_api():
    """
    Allow the user to join the team
    """
    
    # Get data and check if it's valid
    data = request.get_json()
    selected_team_id = data.get("team_id")

    is_valid_id = db.execute("SELECT id FROM teams WHERE id = ?", selected_team_id)

    # If so, add user to the team
    if is_valid_id:
        
        is_already_member = db.execute("SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?", selected_team_id, session["user_id"])
        if is_already_member:
            return jsonify({"success": False, "error": "You are already a member of this team!"})

        membership_count = db.execute("SELECT COUNT(user_id) FROM team_members WHERE user_id = ?", session["user_id"])[0]["COUNT(user_id)"]
        if membership_count >= 20:
            return jsonify({"success": False, "error": "To join a team, you must leave another! Team membership is limited to 20 teams!"})

        db.execute("""
            INSERT INTO 
            team_members (team_id, user_id, privilege) 
            VALUES (?, ?, 'read')
            """, selected_team_id, session["user_id"])

        team_name = db.execute("SELECT name FROM teams WHERE id = ?", selected_team_id)[0]["name"]
        if team_name:
            flash(f"Successfully joined {team_name}!")
            return jsonify({"success": True})
        return jsonify({"success": False, 
                        "error": "An error occurred, please try again!"})

    return jsonify({"success": False, "error": "Invalid team ID, please try again!"})


@app.route("/teams", methods=["GET"])
@login_required
def teams():
    """
    View all teams user is a member of
    """
    
    # Check if user has searched a specific name
    search_query = request.args.get("search", "")

    # If they have find teams with that name
    if search_query:
        teams = db.execute("""
            SELECT teams.id, teams.name, teams.description, teams.code, teams.access_type, team_members.privilege,
                (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
            FROM teams
            JOIN team_members ON teams.id = team_members.team_id
            WHERE team_members.user_id = ?
            AND teams.name LIKE ?
            ORDER BY team_members.privilege, teams.name ASC
            """, session["user_id"], f"%{search_query}%")
        
    else:
        teams = db.execute("""
            SELECT teams.id, teams.name, teams.description, teams.code, teams.access_type, team_members.privilege,
                (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
            FROM teams
            JOIN team_members ON teams.id = team_members.team_id
            WHERE team_members.user_id = ?
            ORDER BY team_members.privilege, teams.name ASC
            """, session["user_id"])

    return render_template("teams.html", teams=teams)


@app.route("/create_team", methods=["GET"])
@login_required
def create_team():
    """
    Show the teams page with the create team form open
    """
    
    teams = db.execute("""
        SELECT teams.id, teams.name, teams.description, teams.code, teams.access_type, team_members.privilege,
            (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
        FROM teams
        JOIN team_members ON teams.id = team_members.team_id
        WHERE team_members.user_id = ?
        ORDER BY team_members.privilege
    """, session["user_id"])
    
    return render_template("teams.html", teams=teams, method="get_create_team")

@app.route("/create_team_api", methods=["POST"])
@api_login_required
def create_team_api():
    """
    Create the requested team with user given data
    """
    
    # Get the data
    data = request.get_json()
    team_name = data.get("team_name")
    team_code = data.get("team_code")
    team_description = data.get("team_description")
    team_access_type = data.get("team_access_type")

    membership_count = db.execute("SELECT COUNT(user_id) FROM team_members WHERE user_id = ?", session["user_id"])[0]["COUNT(user_id)"]
    if membership_count >= 20:
        return jsonify({"success": False, "error": "To create a team, you must leave another team! Team membership is limited to 20 teams!"})

    # Check if necessary fields are filled
    if not team_name or team_name.strip() == "":
        return jsonify({"success": False, 
                        "error": "Missing team name for team creation!"})
    
    if not team_access_type or team_access_type.strip() == "":
        return jsonify({"success": False, 
                        "error": "Missing team status for team creation!"})

    # If the team code is not provided, generate a random one
    if not team_code or team_code.strip() == "":
        team_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    
    # Name length requirement filter
    if len(team_name) > 30:
        return jsonify({"success": False, 
                        "error": f"Team name contains {len(team_name)} characters, limit is 30!"})
    
    if len(team_name) < 7:
        return jsonify({"success": False, 
                        "error": f"Team name contains {len(team_name)} characters, must be at least 7 characters long!"})

    taken = db.execute("SELECT 1 FROM teams WHERE name = ?", team_name)

    # If taken, return such
    if taken:
        return jsonify({"success": False, 
                        "error": "Desired name is already taken!"})
    
    # Code length requirement filter
    if len(team_code) > 12:
        return jsonify({"success": False, 
                        "error": f"Team code contains {len(team_code)} characters, limit is 12!"})

    if team_code and len(team_code) < 6:
        return jsonify({"success": False, 
                        "error": f"Team code contains {len(team_code)} characters, must be at least 6 characters long!"})

    # Check description length if provided
    if team_description and len(team_description) > 500:
        return jsonify({"success": False, 
                        "error": f"Team description contains {len(team_description)} characters, limit is 500!"})

    # Check if access type is valid
    if team_access_type not in ("public", "private"):
        return jsonify({"success": False, 
                        "error": "Invalid team status!"})
    
    # If all is well create the new team and add the user as admin
    new_team_id = db.execute("INSERT INTO teams (name, code, description, access_type) VALUES (?, ?, ?, ?)", team_name, team_code, team_description, team_access_type)
    
    success = db.execute("INSERT INTO team_members (team_id, user_id, privilege) VALUES (?, ?, ?)", new_team_id, session["user_id"], "admin")
    
    if success:
        flash(f"Successfully created {team_name}!")
        return jsonify({"success": True})
    return jsonify({"success": False, 
                    "error": "An error occurred, please try again!"})


@app.route("/manage_team/<string:team_name>", methods=["GET"])
@admin_required
def manage_team(team_name):
    """
    Allow user to manage teams that they are an admin in
    """
    
    search_query = request.args.get("search", "")

    team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)[0]
    members = db.execute("""SELECT users.username, team_members.user_id, team_members.privilege 
                            FROM team_members 
                            JOIN users ON team_members.user_id = users.id 
                            WHERE team_members.team_id = ? 
                            AND users.username LIKE ?
                            ORDER BY users.username ASC
                            """, team["id"], f"%{search_query}%")

    if search_query:
        return render_template("manage_team.html", team=team, current_user=session["user_id"], members=members, method="get_search_member")
    else:
        return render_template("manage_team.html", team=team, current_user=session["user_id"], members=members)

@app.route("/manage_team_api/<string:team_name>", methods=["POST"])
@api_admin_required
def manage_team_api(team_name):
    """
    Make requested team changes with user given data
    """
    
    # Get the requested team data and the current data, use whichever isn't null
    # however requested team data is of higher priority
    data = request.get_json()

    team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)[0]["id"]

    current_data = db.execute("SELECT * FROM teams WHERE id = ?", team_id)[0]

    team_name = data.get("team_name") or team_name
    team_code = data.get("team_code") or current_data["code"]
    team_description = data.get("team_description") or current_data["description"]
    team_access_type = data.get("team_access_type") or current_data["access_type"]

    # Name length requirement filter
    if len(team_name) > 30:
        return jsonify({"success": False, 
                        "error": f"Team name contains {len(team_name)} characters, limit is 30!"})
    
    if len(team_name) < 7:
        return jsonify({"success": False, 
                        "error": f"Team name contains {len(team_name)} characters, must be at least 7 characters long!"})

    # Check if name is taken
    if team_name != current_data["name"]:
        taken = db.execute("SELECT 1 FROM teams WHERE name = ?", team_name)    
        if taken:
            return jsonify({"success": False, 
                            "error": "Desired name is already taken!"})
    
    # Check if code is valid
    if len(team_code) > 12:
        return jsonify({"success": False, 
                        "error": f"Team code contains {len(team_code)} characters, limit is 12!"})

    if team_code and len(team_code) < 6:
        return jsonify({"success": False, 
                        "error": f"Team code contains {len(team_code)} characters, must be at least 6 characters long!"})

    # Check description length if provided
    if team_description and len(team_description) > 500:
        return jsonify({"success": False, 
                        "error": f"Team description contains {len(team_description)} characters, limit is 500!"})

    # Check if the access type is valid
    if team_access_type not in ("public", "private"):
        return jsonify({"success": False, 
                        "error": "Invalid team status!"})
    
    
    # If all is well create the new team and add the user as admin
    success = db.execute("UPDATE teams SET name = ?, code = ?, description = ?, access_type = ? WHERE id = ?", team_name, team_code, team_description, team_access_type, team_id)
    
    if success:
        flash(f"Successfully updated team name to {team_name}!")
        return jsonify({"success": True, 
                        "redirect": f"/manage_team/{team_name}"})
        
    return jsonify({"success": False, 
                    "error": "An error occurred, please try again!"})


@app.route("/manage_member_api/<string:team_name>", methods=["POST"])
@api_admin_required
def manage_member_api(team_name):
    """
    Allow the user to manage the members of a team they are an admin in
    """
    
    # The reason team_name is an argument is that @api_admin_required requires it, I could make
    # it work without that, but if it works don't fix it as it's not a big problem

    # Get the request data
    data = request.get_json()
    member_id = data.get("member_id")
    new_privilege = data.get("privilege")
    
    team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)
    
    # Check if the privilege was given and is valid
    if not new_privilege:
        return jsonify({"success": False, 
                        "error": "No privilege level provided!"})

    if new_privilege not in ["admin", "edit", "read", "kick"]:
        return jsonify({"success": False, 
                        "error": "Invalid privilege level!"})

    # Check if the member ID was given and is valid
    if not member_id:
        return jsonify({"success": False, 
                        "error": "No member ID provided!"})
        
    if member_id == str(session["user_id"]):
        return jsonify({"success": False, 
                        "error": "You cannot change your own privilege level!"})
    
    # Check if the modified user is actually a member of the team
    valid_member = db.execute("SELECT user_id FROM team_members WHERE team_id = ? AND user_id = ?", team_id, member_id)
    if not valid_member:
        return jsonify({"success": False, 
                        "error": "Member not found in this team!"})
        
    member_name = db.execute("SELECT username FROM users WHERE id = ?", member_id)[0]["username"]
    
    # Validate and update member privilege
    if new_privilege == "kick":
        success = db.execute("DELETE FROM team_members WHERE team_id = ? AND user_id = ?", team_id, member_id)
        if success:
            flash(f"Successfully kicked {member_name} from team!")
            return jsonify({"success": True})    
        return jsonify({"success": False, 
                        "error": "An error occurred, please try again!"})

    success = db.execute("UPDATE team_members SET privilege = ? WHERE team_id = ? AND user_id = ?", new_privilege, team_id, member_id)
    if success:
        flash(f"Successfully updated {member_name}'s privilege to {new_privilege}!")
        return jsonify({"success": True})
    return jsonify({"success": False, 
                    "error": "An error occurred, please try again!"})


@app.route("/delete_team_api/<string:team_name>", methods=["POST"])
@api_admin_required
def delete_team_api(team_name):
    """
    Allow the user to delete the teams they are an admin in
    """

    if not team_name:
        return jsonify({"success": False, "error": 
                        "No team name provided!"})
        
    team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)[0]["id"]

    exists = db.execute("SELECT id FROM teams WHERE id = ?", team_id)
    if exists:
        success = db.execute("DELETE FROM teams WHERE id = ?", team_id)
        if success:
            flash(f"Successfully deleted {team_name}!")
            return jsonify({"success": True})
        return jsonify({"success": False, 
                        "error": "An error occurred, please try again!"})

    return jsonify({"success": False, 
                    "error": "Team not found, please try again!"})


@app.route("/edit_team/<string:team_name>", methods=["GET"])
@edit_required
def edit_team(team_name):
    """
    Show the edit team page
    """
    
    topics = db.execute("""
        SELECT topics.name, teams.name
        FROM topics 
        JOIN team_topics ON topics.id = team_topics.topic_id
        JOIN teams ON team_topics.team_id = teams.id
        WHERE teams.name = ?
        ORDER BY topics.name
    """, team_name)

    team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)[0]

    return render_template("edit_team.html", topics=topics, team=team)

@app.route("/create_topic_api/<string:team_name>", methods=["POST"])
@api_edit_required
def create_topic_api(team_name):
    # Get the data
    
    data = request.get_json()
    topic_name = data.get("topic_name").strip()
    
    if not topic_name:
        return jsonify({"success": False, 
                        "error": "Please provide a topic name!"})

    name_length = len(topic_name)

    if name_length > 30:
        return jsonify({"success": False, 
                        "error": f"Topic name is {name_length} characters, limit is 30!"})
    
    if name_length < 7:
        return jsonify({"success": False, 
                        "error": f"Topic name is {name_length} characters, minimum is 7 characters!"})

    team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)[0]["id"]

    # Create the new topic
    topic_id = db.execute("INSERT INTO topics (name) VALUES (?)", topic_name)
    success = db.execute("INSERT INTO team_topics (team_id, topic_id) VALUES (?, ?)", team_id, topic_id)
    if success:
        flash(f"Successfully created {topic_name}!")
        return jsonify({"success": True})
    return jsonify({"success": False, 
                    "error": "An error occurred, please try again!"})


@app.route("/edit_topic_api/<string:team_name>/<string:topic_name>", methods=["POST"])
@api_edit_required
def edit_topic_api(team_name, topic_name):
    
    data = request.get_json()
    requested_name = data.get("new_name").strip()
    
    if not requested_name:
        return jsonify({"success": False,
                        "error": "Please provide a new name!"})
        
    team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)

    team_id = team_id[0]["id"]

    # Check if the topic exists
    topic_id = db.execute("SELECT id FROM topics WHERE name = ? AND team_id = ?", topic_name, team_id)[0]["id"]
    if not topic_id:
        return jsonify({"success": False, 
                        "error": "Topic does not exist!!"})
        
    name_length = len(requested_name)
    
    if name_length > 30:
        return jsonify({"success": False,
                        "error": f"Team name contains {name_length} characters, limit is 30!"})
    if name_length < 7:
        return jsonify({"success": False,
                        "error": f"Team name contains {name_length} characters, must be at least 7 characters!"})

    # Update the topic name
    success = db.execute("UPDATE topics SET name = ? WHERE id = ?", requested_name, topic_id)
    if success:
        flash(f"Successfully updated topic to {requested_name}!")
        return jsonify({"success": True})
    return jsonify({"success": False,
                    "error": "An error occurred, please try again!"})


@app.route("/join_code", methods=["GET"])
@login_required
def join_code():
    """
    Show the teams page with the join code modal already opened
    """

    teams = db.execute("""
        SELECT teams.id, teams.name, teams.description, teams.code, teams.access_type, team_members.privilege,
            (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
        FROM teams
        JOIN team_members ON teams.id = team_members.team_id
        WHERE team_members.user_id = ?
        GROUP BY teams.id
        ORDER BY team_members.privilege
    """, session["user_id"])
    return render_template("teams.html", teams=teams, method="get_join_code")

@app.route("/join_code_api", methods=["POST"])
@api_login_required
def join_code_api():
    """
    Join a team with the given name and code
    """

    # Get the data
    data = request.get_json()
    team_name = data.get("team_name")
    team_code = data.get("team_code")

    membership_count = db.execute("SELECT COUNT(user_id) FROM team_members WHERE user_id = ?", session["user_id"])[0]["COUNT(user_id)"]
    if membership_count >= 20:
        return jsonify({"success": False, "error": "To join a team, you must leave another! Team membership is limited to 20 teams!"})

    # Check if the provided name and code are valid
    selected_team_result = db.execute("SELECT id FROM teams WHERE name = ? AND code = ?", team_name, team_code)
    if selected_team_result:
        selected_team_id = selected_team_result[0]["id"]
        already_in_team = db.execute("SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?", selected_team_id, session["user_id"])
        
        if already_in_team:
            return jsonify({"success": False, 
                            "error": "You are already a member of this team!"})
        
        # If all is well create the new team and add the user
        success = db.execute("INSERT INTO team_members (team_id, user_id, privilege) VALUES (?, ?, 'read')", selected_team_id, session["user_id"])
        if success:
            flash(f"Successfully joined team {team_name}!")
            return jsonify({"success": True})
        return jsonify({"success": False,
                        "error": "An error occurred, please try again!"})

    return jsonify({"success": False,
                    "error": "Invalid team name or code, please make sure you enter the correct information and try again"})


@app.route("/leave_team_api/<string:team_name>", methods=["POST"])
@api_login_required
def leave_team_api(team_name):
    """
    Allow users to leave a team
    """
    
    data = request.get_json()
    team_id = data.get("team_id")

    privilege = db.execute("SELECT privilege FROM team_members WHERE user_id = ? AND team_id = ?", session["user_id"], team_id)[0]["privilege"]

    team_info = db.execute("""SELECT COUNT(team_members.team_id), teams.name FROM team_members 
                            JOIN teams ON team_members.team_id = teams.id WHERE team_members.team_id = ?""", team_id)[0]
    
    member_count = team_info["COUNT(team_members.team_id)"]

    # If the user is an admin, check if they are able to leave the team
    if privilege == "admin":
        if member_count == 1:
            return jsonify({"success": False, 
                            "error": "Admins cannot leave the team if they are the last member, please delete the team instead!", "name": team_name})
        
        admin_count = db.execute("SELECT COUNT(privilege) FROM team_members WHERE team_id = ? AND privilege = 'admin'", team_id)[0]["COUNT(privilege)"]
        if admin_count == 1:
            return jsonify({"success": False, 
                            "error": "Admins cannot leave the team if they are the last admin! Please delete the team, or pass on admin privileges instead!", "name": team_name})

    is_member = db.execute("SELECT FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])
    
    if is_member:
        success = db.execute("DELETE FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])
        
        if success:
            flash(f"Successfully left {team_name}")
            return jsonify({"success": True})   

        return jsonify({"success": False, 
                        "error": "An error occurred, please try again!"})

    return jsonify({"success": False,
                    "error": "You are not a member of this team!"})


@app.route("/team/<string:team_name>", methods=["GET"])
@membership_required
def team_page(team_name):
    """
    View a team's page
    """
    
    topics = db.execute("""
        SELECT topics.id, topics.name, teams.name AS team_name
        FROM topics 
        JOIN team_topics ON topics.id = team_topics.topic_id
        JOIN teams ON team_topics.team_id = teams.id
        WHERE teams.name = ?
        ORDER BY topics.name
    """, team_name)

    return render_template("team_page.html", topics=topics)
    
"""
Logic and route block end regarding team viewing, team creation, team leaving, and team management.
"""



"""
Logic and route block end regarding board viewing and management.
"""
@app.route("/team/<string:team_name>/topic/<string:topic_name>")
@membership_required
def board(team_name, topic_name):
    statuses = [
        {"id": "announcement", "name": "Announcements"},
        {"id": "todo", "name": "To Do"},
        {"id": "doing", "name": "Doing"},
        {"id": "done", "name": "Done"}
    ]
    
    user_privilege = db.execute("""SELECT privilege FROM team_members
                                JOIN teams ON team_members.team_id = teams.id
                                WHERE team_members.user_id = ?
                                AND teams.name = ?""", session["user_id"], team_name)[0]["privilege"]
    
    if user_privilege in ['admin', 'edit']:
        statuses.append({"id": "delete", "name": "DELETE"})

    cards = db.execute("""
        SELECT notes.id, notes.content, notes.status, topic_notes.topic_id
        FROM notes
        JOIN topic_notes ON notes.id = topic_notes.note_id
        JOIN team_topics ON topic_notes.topic_id = team_topics.topic_id
        JOIN topics ON team_topics.topic_id = topics.id
        JOIN teams ON team_topics.team_id = teams.id
        WHERE teams.name = ?
        AND topics.name = ?
    """, team_name, topic_name)

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

    return jsonify({"status": True})
"""
Logic and route block end regarding board viewing and management.
"""


if __name__ == "__main__":
    app.run(debug=True)
