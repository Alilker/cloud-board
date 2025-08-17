import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, membership_required, db
from random import SystemRandom
import os
import string
import re

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.environ.get("SECRET_KEY", "Supersecretkey")
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


""" 
User account logic and route block start for logging in, registering, and changing username or password.
"""
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log user in
    """

    next_url = request.args.get("next")
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Handle JSON request (for AJAX form submission)
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        next_url = data.get("next_url")
        
        # Ensure username was submitted
        if not username:
            return jsonify({"success": False, 
                            "error": "must provide username"})

        # Ensure password was submitted
        elif not password:
            return jsonify({"success": False, 
                            "error": "must provide password"})

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], password
        ):
            return jsonify({"success": False, 
                            "error": "invalid username and/or password"})

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        if not next_url:
            next_url = "/"
            
        # Return success
        return jsonify({"success": True, "redirect": next_url})

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():    
    """
    Register new user
    """
    
    # Clear any existing session
    session.clear()

    # User reached route via GET
    if request.method == "GET":
        return render_template("register.html")
    
    # User reached route via POST
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    confirmation = data.get("confirmation")
    
    # Collect all validation errors
    errors = []
    
    # Username validation
    if not username:
        errors.append("Missing username!")
    else:
        
        # Validate username length requirements
        username_length = len(username)
        if username_length > 15:
            errors.append(f"Username is {username_length} characters, limit is 15!")
        elif username_length < 5:
            errors.append(f"Username is {username_length} characters, must be at least 5 characters!")
        else:
            
            # Check if username is already taken
            existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
            if existing_user:
                errors.append("Username is already taken!")

    # Password validation
    if not password:
        errors.append("Missing password!")
    else:
        
        # Validate password length and pattern requirements
        password_length = len(password)
        pattern = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}"
        
        if password_length > 20:
            errors.append(f"Password is {password_length} characters, limit is 20!")
        elif password_length < 8:
            errors.append(f"Password is {password_length} characters, must be at least 8 characters!")
        elif not re.match(pattern, password):
            errors.append("Password must contain at least one number, one uppercase letter, and one lowercase letter!")
        else:
            
            # Check password confirmation
            if not confirmation:
                errors.append("Missing password confirmation!")
            elif confirmation != password:
                errors.append("Passwords don't match!")

    # Return errors if any
    if errors:
        return jsonify({"success": False, 
                        "errors": errors})

    # Create user account
    user_id = db.execute(
        "INSERT INTO users (username, hash) VALUES (?, ?)", 
        username, 
        generate_password_hash(password)
    )

    # Log in the new user
    session["user_id"] = user_id
    session["username"] = username

    # Return success response
    return jsonify({"success": True, "redirect": "/"})

@app.route("/register_check_username", methods=["POST"])
def register_check_username():
    """
    Check if username is available for registration
    """
    
    data = request.get_json()
    username = data.get("username")
    
    # Check if username is provided
    if not username or username.strip() == "":
        return jsonify({"success": False, 
                        "error": "Username is required!"})
    
    # Check if username is taken by another user
    user_exists = db.execute("SELECT 1 FROM users WHERE username = ?", username)
    if user_exists:
        return jsonify({"success": False, 
                        "error": "Username is already taken!"})
    
    # Validate username length requirements
    user_length = len(username)
    if user_length > 15:
        return jsonify({"success": False, 
                        "error": f"Username is {user_length} characters, limit is 15!"})
    
    if user_length < 5:
        return jsonify({"success": False, 
                        "error": f"Username is {user_length} characters, must be at least 5 characters"})

    return jsonify({"success": True})


@app.route("/register_check_password", methods=["POST"])
def register_check_password():
    """
    Check if password is valid for registration
    """
    
    data = request.get_json()
    password = data.get("password")

    # Check if password is provided
    if not password:
        return jsonify({"success": False, 
                        "error": "Password is required!"})
    
    # Validate password length and pattern requirements
    password_length = len(password)
    pattern = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}"

    if password_length > 20:
        return jsonify({"success": False, 
                        "error": f"Password is {password_length} characters, limit is 20!"})

    if password_length < 8:
        return jsonify({"success": False, 
                        "error": f"Password is {password_length} characters, must be at least 8 characters"})

    if not re.match(pattern, password):
        return jsonify({"success": False, 
                        "error": "Password must contain at least one number, one uppercase letter, and one lowercase letter."})

    return jsonify({"success": True})

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    Allow user to change account password and username
    """
    
    # User reached route via GET
    if request.method == "GET":
        return render_template("account.html")
    
    # User reached route via POST
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
    errors = []
    
    # Username validation
    username_valid = True
    if new_username and new_username.strip():
        has_changes = True
        
        # Validate username length requirements
        username_length = len(new_username)
        if username_length > 15:
            errors.append(f"Username is {username_length} characters, limit is 15!")
            username_valid = False
        elif username_length < 5:
            errors.append(f"Username is {username_length} characters, must be at least 5 characters!")
            username_valid = False
        else:
            # Check if username is taken (excluding current user's username)
            current_username = session.get("username")
            if new_username != current_username:
                existing_user = db.execute("SELECT * FROM users WHERE username = ?", new_username)
                if existing_user:
                    errors.append("Username is already taken!")
                    username_valid = False
    
    # Password validation
    password_valid = True
    if new_password and new_password.strip():
        has_changes = True
        
        # Validate password length and pattern requirements
        password_length = len(new_password)
        pattern = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}"
        
        if password_length > 20:
            errors.append(f"Password is {password_length} characters, limit is 20!")
            password_valid = False
        elif password_length < 8:
            errors.append(f"Password is {password_length} characters, must be at least 8 characters!")
            password_valid = False
        elif not re.match(pattern, new_password):
            errors.append("Password must contain at least one number, one uppercase letter, and one lowercase letter!")
            password_valid = False
        else:
            # Check password confirmation
            if not confirmation or confirmation.strip() == "":
                errors.append("Please confirm your new password!")
                password_valid = False
            elif new_password != confirmation:
                errors.append("New passwords do not match!")
                password_valid = False
    
    # Check if any changes were requested
    if not has_changes:
        return jsonify({"success": False, 
                        "error": "No changes were made. Please enter a new username or password!"})
    
    # Return errors if any
    if errors:
        return jsonify({"success": False, 
                        "errors": errors})
    
    # All validations passed - apply changes
    if new_username and new_username.strip() and username_valid:
        db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, user_id)
        session["username"] = new_username
    
    if new_password and new_password.strip() and password_valid:
        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, user_id)
    
    flash("Successfully made changes!")
    return jsonify({"success": True, "redirect": True})


@app.route("/account_check_username", methods=["POST"])
def account_check_username():
    """
    Check username for account modification
    """

    data = request.get_json()
    username = data.get("username")

    # Return success if no username provided as it's optional
    if not username or username.strip() == "":
        return jsonify({"success": True})
    
    # Get current user's username to keep it
    current_username = session.get("username")
    
    # If it's the same as current username, allow it
    if username == current_username:
        return jsonify({"success": True})
    
    # Check if username is taken by another user
    user_exists = db.execute("SELECT 1 FROM users WHERE username = ?", username)
    if user_exists:
        return jsonify({"success": False, 
                        "error": "Username is already taken!"})
    
    # Validate username length requirements
    user_length = len(username)
    if user_length > 15:
        return jsonify({"success": False,
                        "error": f"Username is {user_length} characters, limit is 15!"})
    
    if user_length < 5:
        return jsonify({"success": False,
                        "error": f"Username is {user_length} characters, must be at least 5 characters"})
    
    return jsonify({"success": True})


@app.route("/account_check_password", methods=["POST"])
def account_check_password():
    """
    Check password for account modification
    """
    
    data = request.get_json()
    password = data.get("password")

    # Return success if no password provided as it's optional
    if not password:
        return jsonify({"success": True})
    
    # Validate password length and pattern requirements
    password_length = len(password)
    pattern = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}"

    if password_length > 20:
        return jsonify({"success": False, 
                        "error": f"Password is {password_length} characters, limit is 20!"})

    if password_length < 8:
        return jsonify({"success": False, 
                        "error": f"Password is {password_length} characters, must be at least 8 characters"})

    if not re.match(pattern, password):
        return jsonify({"success": False, 
                        "error": "Password must contain at least one number, one uppercase letter, and one lowercase letter."})

    return jsonify({"success": True})


@app.route("/logout")
def logout():
    """
    Log user out
    """

    # Forget any user id
    session.clear()

    # Redirect user to the index page
    return redirect("/")

""" 
User account logic and route block end for logging in, registering, and changing username or password.
"""



"""
Logic and route block start regarding team viewing, team creation, team leaving, and team management.
"""
@app.route("/explore", methods=["GET", "POST"])
@login_required
def explore_teams():
    """
    Allow user to explore public teams and join them
    """
    
    # Check if user has searched a specific name
    search_query = request.args.get("search", "")

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        if search_query:
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
            AND teams.name LIKE ?
            GROUP BY teams.id
            ORDER BY member_count DESC
            """, session["user_id"], f"%{search_query}%")
        
        else:
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

    # If user reached route via POST
    if request.method == "POST":
        
        # Get team ID and see if its valid
        team_id = request.form.get("team_id")
        selected_team = next((team for team in teams if str(team["id"]) == team_id), None)
        
        # If so, add user to the team
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
        return render_template("explore.html", teams=teams)

@app.route("/teams", methods=["GET"])
@login_required
def view_teams():
    """
    View all teams user is a member of
    """
    
    # Check if user has searched a specific name
    search_query = request.args.get("search", "")

    # If they have find teams with that name
    if search_query:
        teams = db.execute("""
            SELECT teams.id, teams.name, teams.description, team_members.privilege,
                (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
            FROM teams
            JOIN team_members ON teams.id = team_members.team_id
            WHERE team_members.user_id = ?
            AND teams.name LIKE ?
            ORDER BY team_members.privilege
            """, session["user_id"], f"%{search_query}%")
        
    else:
        teams = db.execute("""
            SELECT teams.id, teams.name, teams.description, team_members.privilege,
                (SELECT COUNT(*) FROM team_members WHERE team_members.team_id = teams.id) AS member_count
            FROM teams
            JOIN team_members ON teams.id = team_members.team_id
            WHERE team_members.user_id = ?
            ORDER BY team_members.privilege
            """, session["user_id"])

    return render_template("teams.html", teams=teams)

@app.route("/create_team", methods=["GET", "POST"])
@login_required
def create_team():
    """
    Allow users to create new teams
    """

    # If user reached route via GET, render the teams page but with the modal already open
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
        return render_template("teams.html", teams=teams, method="get")

    # If user reached route via POST, create the team
    else:
        team_name = request.form.get("team-name")
        team_code = request.form.get("team-code")
        team_description = request.form.get("team-description")
        team_access_type = request.form.get("team-access-type")

        # Check if necessary fields are filled
        for field_name, field_value in [("team name", team_name), ("team status", team_access_type)]:
            if field_value is None or field_value.strip() == "":
                return render_template("error.html", error=f"Missing {field_name} for team creation!")

        # If the team code is not provided, generate a random one
        if team_code == "":
            team_code = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
        
        # Name length requirement filter
        if len(team_name) > 30:
            return render_template("error.html", error=f"Team name contains {len(team_name)} characters, limit is 30!")
        
        if len(team_name) < 7:
            return render_template("error.html", error=f"Team name contains {len(team_name)} characters, must be at least 7 characters long!")

        taken = db.execute("SELECT 1 FROM teams WHERE name = ?", team_name)

        # If taken, return such
        if taken:
            return render_template("error.html", error="Desired name is already taken!")
        
        if len(team_code) > 12:
            return render_template("error.html", error=f"Team code contains {len(team_code)} characters, limit is 12!")

        if team_access_type not in ("public", "private"):
            return render_template("error.html", error="Invalid team status")
        
        # If all is well create the new team and add the user as admin
        db.execute("INSERT INTO teams (name, code, description, access_type) VALUES (?, ?, ?, ?)", team_name, team_code, team_description, team_access_type)
        new_team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)[0]["id"]
        
        db.execute("INSERT INTO team_members (team_id, user_id, privilege) VALUES (?, ?, ?)", new_team_id, session["user_id"], "admin")
        
        flash(f"Successfully created {team_name}!")
        return redirect("/teams")

@app.route("/create_check_name", methods=["POST"])
@login_required
def create_check_name():
    """
    Check if the team name is valid for creation
    """
    name = request.get_json()
    team_name = name.get("name")
    if not team_name:
        return jsonify({
            "success": False,
            "error": "Team name can't be blank"
        })

    taken = db.execute("SELECT 1 FROM teams WHERE name = ?", team_name)

    # If taken, return such
    if taken:
        return jsonify({
            "success": False,
            "error": "Desired name is already taken!"
        })

    # Check length requirements
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

@app.route("/create_check_code", methods=["POST"])
def create_check_code():
    """
    Check if the team code is valid for creation
    """
    
    data = request.get_json()
    team_code = data.get("code")

    team_code_length = len(team_code)

    # Check if team code is provided, return success if its blank as it's optional
    if not team_code_length:
        return jsonify({
            "success": True,
        })

    # Check length requirements
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
    
@app.route("/create_check_description", methods=["POST"])
def create_check_description():
    """
    Check if the team description is valid for creation
    """
    
    data = request.get_json()
    team_description = data.get("description")

    # Check if the description length meets requirements
    team_description_length = len(team_description)
    if team_description_length > 500:
        return jsonify({
            "success": False,
            "error": f"Team description contains {team_description_length} characters, limit is 500!"
        })
        
    else:
        return jsonify({"success": True})
    
@app.route("/join_code", methods=["POST"])
@login_required
def join_code():
    """
    Join a team with the given name and code
    """
    
    data = request.get_json()
    team_name = data.get("team_name")
    team_code = data.get("team_code")

    # Check if the provided name and code are valid
    selected_team_result = db.execute("SELECT id FROM teams WHERE name = ? AND code = ?", team_name, team_code)
    if selected_team_result:
        selected_team_id = selected_team_result[0]["id"]
        already_in_team = db.execute("SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?", selected_team_id, session["user_id"])
        
        if already_in_team:
            return jsonify({"success": False, 
                            "error": "You are already a member of this team!"})
        
        # If all is well create the new team and add the user
        db.execute("INSERT INTO team_members (team_id, user_id, privilege) VALUES (?, ?, 'read')", selected_team_id, session["user_id"])
        flash("Successfully joined team!")
        return jsonify({"success": True})
    
    else:
        return jsonify({"success": False, "error": "Invalid team name or code, please make sure you enter the correct information and try again"})

@app.route("/join_check_name", methods=["POST"])
@login_required
def join_check_name():
    """
    Check if the team name is valid for joining
    """
    
    name = request.get_json()
    team_name = name.get("name")

    # Check if team name is provided
    if not team_name:
        return jsonify({
            "success": False,
            "error": "Team name can't be blank"
        })

    # Check length requirements
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

@app.route("/join_check_code", methods=["POST"])
def join_check_code():
    """
    Check if the team code is valid for joining
    """
    
    data = request.get_json()
    team_code = data.get("code")

    # Check if team code is provided
    if not team_code:
        return jsonify({"success": False, 
                        "error": "Team code can't be blank"})

    # Check length requirements
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
    """
    Allow users to leave a team
    """
    
    data = request.get_json()
    team_id = data.get("team_id")

    privilege = db.execute("SELECT privilege FROM team_members WHERE user_id = ? AND team_id = ?", session["user_id"], team_id)[0]["privilege"]

    # If the user is an admin, check if they are able to leave the team
    if privilege == "admin":
        team_info = db.execute("""SELECT COUNT(team_members.team_id), teams.name FROM team_members 
                                JOIN teams ON team_members.team_id = teams.id WHERE team_members.team_id = ?""", team_id)[0]
        
        member_count = team_info["COUNT(team_members.team_id)"]
        team_name = team_info["name"]
        
        if member_count == 1:
            return jsonify({"success": False, "error": "Admins cannot leave the team if they are the last member, please delete the team instead.", "name": team_name})
        
        admin_count = db.execute("SELECT COUNT(privilege) FROM team_members WHERE team_id = ? AND privilege = 'admin'", team_id)[0]["COUNT(privilege)"]
        if admin_count == 1:
            return jsonify({"success": False, "error": "Admins cannot leave the team if they are the last admin. Please delete the team, or pass on admin privileges instead.", "name": team_name})

    left_team_count = db.execute("DELETE FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])
    if left_team_count == 0:
        return jsonify({"success": False})
    flash("Successfully left teams")
    return jsonify({"success": True})

@app.route("/team/<string:team_name>")
@membership_required
def team_page(team_name):
    """
    Allow users to view a team's page
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
        JOIN teams ON team_topics.team_id = teams.id
        WHERE teams.name = ?
        AND topics.name = ?
    """, team_name, topic_name.capitalize())

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


"""
Logic and route block end regarding board viewing and management.
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
