import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, membership_required, admin_required, db
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
# Logging in, account managing, registering, and logging out have been
# adapted from CS50's finance problem set
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log user in
    """
    
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
                            "error": "Invalid username and/or password"})

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

            
        # Return success
        return jsonify({"success": True})

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
            return jsonify({"success": False, 
                            "error": f"Username is {username_length} characters, limit is 15!"})
        elif username_length < 5:
            return jsonify({"success": False, 
                            "error": f"Username is {username_length} characters, must be at least 5 characters!"})
        else:
            
            # Check if username is already taken
            existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
            if existing_user:
                return jsonify({"success": False, 
                                "error": "Username is already taken!"})

    # Password validation
    if not password:
        return jsonify({"success": False, 
                        "error": "Missing password!"})
    else:
        
        # Validate password length and pattern requirements
        password_length = len(password)
        pattern = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}"
        
        if password_length > 20:
            return jsonify({"success": False, 
                            "error": f"Password is {password_length} characters, limit is 20!"})
        elif password_length < 8:
            return jsonify({"success": False, 
                            "error": f"Password is {password_length} characters, must be at least 8 characters!"})
        elif not re.match(pattern, password):
            return jsonify({"success": False, 
                            "error": "Password must contain at least one number, one uppercase letter, and one lowercase letter!"})
        else:
            
            # Check password confirmation
            if not confirmation:
                return jsonify({"success": False, 
                                "error": "Missing password confirmation!"})
            elif confirmation != password:
                return jsonify({"success": False, 
                                "error": "Passwords don't match!"})

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
    
    # Username validation
    username_valid = True
    if new_username and new_username.strip():
        has_changes = True
        
        # Validate username length requirements
        username_length = len(new_username)
        if username_length > 15:
            return jsonify({"success": False, 
                            "error": f"Username is {username_length} characters, limit is 15!"})
        elif username_length < 5:
            return jsonify({"success": False, 
                            "error": f"Username is {username_length} characters, must be at least 5 characters!"})
        else:
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
        elif password_length < 8:
            return jsonify({"success": False, 
                            "error": f"Password is {password_length} characters, must be at least 8 characters!"})
        elif not re.match(pattern, new_password):
            return jsonify({"success": False, 
                            "error": "Password must contain at least one number, one uppercase letter, and one lowercase letter!"})
        else:
            # Check password confirmation
            if not confirmation or confirmation.strip() == "":
                return jsonify({"success": False, 
                                "error": "Please confirm your new password!"})
            elif new_password != confirmation:
                return jsonify({"success": False, 
                                "error": "New passwords do not match!"})

    # Check if any changes were requested
    if not has_changes:
        return jsonify({"success": False, 
                        "error": "No changes were made. Please enter a new username or password!"})
    
    # All validations passed - apply changes
    if new_username and new_username.strip() and username_valid:
        db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, user_id)
        session["username"] = new_username
    
    if new_password and new_password.strip() and password_valid:
        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, user_id)
    
    flash("Successfully made changes!")
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
                SELECT teams.id, teams.name, teams.description, teams.code, teams.access_type, COUNT(team_members.user_id) AS member_count
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
                SELECT teams.id, teams.name, teams.description, teams.code, teams.access_type, COUNT(team_members.user_id) AS member_count
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
        selected_team_id = request.form.get("team_id")
        selected_team_name = request.form.get("team_name")

        # If so, add user to the team
        if selected_team_id:
            db.execute("""
                INSERT INTO 
                team_members (team_id, user_id, privilege) 
                VALUES (?, ?, 'read')
                """, selected_team_id, session["user_id"])
            flash(f"You have successfully joined {selected_team_name} ")

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
            SELECT teams.id, teams.name, teams.description, teams.code, teams.access_type, team_members.privilege,
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

    # If user reached route via GET, render the teams page but with the create team modal already open
    if request.method == "GET":
        teams = db.execute("""
            SELECT teams.id, teams.name, teams.description, team_members.privilege, teams.code, teams.access_type, COUNT(team_members.user_id) AS member_count
            FROM teams
            LEFT JOIN team_members
                ON teams.id = team_members.team_id
            WHERE team_members.user_id = ?
            GROUP BY teams.id
            ORDER BY team_members.privilege
            """, session["user_id"])
        return render_template("teams.html", teams=teams, method="get_create_team")

    # If user reached route via POST, create the team
    else:
        data = request.get_json()
        team_name = data.get("team_name")
        team_code = data.get("team_code")
        team_description = data.get("team_description")
        team_access_type = data.get("team_access_type")

        # Check if necessary fields are filled
        if not team_name or team_name.strip() == "":
            return jsonify({"success": False, 
                            "error": "Missing team name for team creation!"})
        
        if not team_access_type or team_access_type.strip() == "":
            return jsonify({"success": False, 
                            "error": "Missing team status for team creation!"})

        # If the team code is not provided, generate a random one
        if not team_code or team_code.strip() == "":
            team_code = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
        
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
        
        if len(team_code) > 12:
            return jsonify({"success": False, 
                            "error": f"Team code contains {len(team_code)} characters, limit is 12!"})

        if team_code and len(team_code) < 6:
            return jsonify({"success": False, 
                            "error": f"Team code contains {len(team_code)} characters, must be at least 6 characters long!"})

        if team_access_type not in ("public", "private"):
            return jsonify({"success": False, 
                            "error": "Invalid team status"})
        
        # Check description length if provided
        if team_description and len(team_description) > 500:
            return jsonify({"success": False, 
                            "error": f"Team description contains {len(team_description)} characters, limit is 500!"})
        
        # If all is well create the new team and add the user as admin
        db.execute("INSERT INTO teams (name, code, description, access_type) VALUES (?, ?, ?, ?)", team_name, team_code, team_description, team_access_type)
        new_team_id = db.execute("SELECT id FROM teams WHERE name = ?", team_name)[0]["id"]
        
        db.execute("INSERT INTO team_members (team_id, user_id, privilege) VALUES (?, ?, ?)", new_team_id, session["user_id"], "admin")
        
        flash(f"Successfully created {team_name}!")
        return jsonify({"success": True})

@app.route("/manage_team/<string:team_name>", methods=["GET", "POST"])
@admin_required
def manage_team(team_name):

    search_query = request.args.get("search", "")
    print(search_query)
    if request.method == "GET":
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)[0]
        members = db.execute("""SELECT users.username, team_members.user_id, team_members.privilege FROM team_members 
                             JOIN users ON team_members.user_id = users.id 
                             WHERE team_members.team_id = ? AND users.username LIKE ?""", team["id"], f"%{search_query}%")
        print(members)

        if search_query:
            return render_template("manage_team.html", team=team, current_user=session["user_id"], members=members, method="get_search_member")
        else:
            return render_template("manage_team.html", team=team, current_user=session["user_id"], members=members)

    else:
        data = request.get_json()
        team_id = data.get("team_id")
        privilege = db.execute("SELECT privilege FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])[0]["privilege"]
        
        if privilege == "admin":
            data = request.get_json()
            team_id = data.get("team_id")
            current_data = db.execute("SELECT * FROM teams WHERE id = ?", team_id)[0]

            team_name = data.get("team_name") or current_data["name"]
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

            if team_name != current_data["name"]:
                taken = db.execute("SELECT 1 FROM teams WHERE name = ?", team_name)
                    
                # If taken, return such
                if taken:
                    return jsonify({"success": False, 
                                    "error": "Desired name is already taken!"})
            
            if len(team_code) > 12:
                return jsonify({"success": False, 
                                "error": f"Team code contains {len(team_code)} characters, limit is 12!"})

            if team_code and len(team_code) < 6:
                return jsonify({"success": False, 
                                "error": f"Team code contains {len(team_code)} characters, must be at least 6 characters long!"})

            if team_access_type not in ("public", "private"):
                return jsonify({"success": False, 
                                "error": "Invalid team status"})
            
            # Check description length if provided
            if team_description and len(team_description) > 500:
                return jsonify({"success": False, 
                                "error": f"Team description contains {len(team_description)} characters, limit is 500!"})
            
            # If all is well create the new team and add the user as admin
            db.execute("UPDATE teams SET name = ?, code = ?, description = ?, access_type = ? WHERE id = ?", team_name, team_code, team_description, team_access_type, team_id)

            flash(f"Successfully updated {team_name}!")
            return jsonify({"success": True, "redirect": f"/manage_team/{team_name}"})
        else:
            return jsonify({"success": False, 
                            "error": "Only admins can edit team details!"})


@app.route("/manage_member/<string:team_name>", methods=["POST"])
@admin_required
def manage_member(team_name):
    data = request.get_json()
    team_id = data.get("team_id")
    member_id = data.get("member_id")
    new_privilege = data.get("privilege")
    
    user_privilege = db.execute("SELECT privilege FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])[0]["privilege"]
    if user_privilege == "admin":

        if not new_privilege:
            return jsonify({"success": False, 
                            "error": "No privilege level provided!"})

        if new_privilege not in ["admin", "edit", "read", "kick"]:
            return jsonify({"success": False, 
                            "error": "Invalid privilege level!"})

        if not member_id:
            return jsonify({"success": False, 
                            "error": "No member ID provided!"})
            
        if member_id == str(session["user_id"]):
            return jsonify({"success": False, 
                            "error": "You cannot change your own privilege level!"})
        
        valid_member = db.execute("SELECT user_id FROM team_members WHERE team_id = ? AND user_id = ?", team_id, member_id)

        if not valid_member:
            return jsonify({"success": False, 
                            "error": "Member not found in this team!"})
            
            
        member_name = db.execute("SELECT username FROM users WHERE id = ?", member_id)[0]["username"]
        if new_privilege == "kick":
            flash(f"Successfully kicked {member_name} from team.")
            db.execute("DELETE FROM team_members WHERE team_id = ? AND user_id = ?", team_id, member_id)

        # Validate and update member privilege
        flash(f"Successfully updated {member_name}'s privilege to {new_privilege}!")
        db.execute("UPDATE team_members SET privilege = ? WHERE team_id = ? AND user_id = ?", new_privilege, team_id, member_id)
        return jsonify({"success": True})
    
    else:
        return jsonify({"success": False, 
                        "error": "Only admins can edit member privileges!"})


@app.route("/delete_team/<string:team_name>", methods=["POST"])
@admin_required
def delete_team(team_name):
    data = request.get_json()
    team_id = data.get("team_id")

    privilege = db.execute("SELECT privilege FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])[0]["privilege"]

    if privilege == "admin":
        db.execute("DELETE FROM teams WHERE id = ?", team_id)
        flash("Team deleted successfully!")
        return jsonify({"success": True})
    
    else:
        return jsonify({"success": False, 
                        "error": "Only admins can delete teams!"})

@app.route("/join_code", methods=["GET", "POST"])
@login_required
def join_code():
    """
    Join a team with the given name and code
    """
    
    # If user reached route via POST, join the team
    if request.method == "POST":
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
            return jsonify({"success": False, 
                            "error": "Invalid team name or code, please make sure you enter the correct information and try again"})
   
    # If user reached route via GET, render the teams page but with the join code modal already open
    else:
        teams = db.execute("""
            SELECT teams.id, teams.name, teams.description, team_members.privilege, teams.code, teams.access_type, COUNT(team_members.user_id) AS member_count
            FROM teams
            LEFT JOIN team_members
                ON teams.id = team_members.team_id
            WHERE team_members.user_id = ?
            GROUP BY teams.id
            ORDER BY team_members.privilege
            """, session["user_id"])
        return render_template("teams.html", teams=teams, method="get_join_code")

@app.route("/leave_team", methods=["POST"])
@login_required
def leave_team():
    """
    Allow users to leave a team
    """
    
    data = request.get_json()
    team_id = data.get("team_id")

    privilege = db.execute("SELECT privilege FROM team_members WHERE user_id = ? AND team_id = ?", session["user_id"], team_id)[0]["privilege"]

    team_info = db.execute("""SELECT COUNT(team_members.team_id), teams.name FROM team_members 
                            JOIN teams ON team_members.team_id = teams.id WHERE team_members.team_id = ?""", team_id)[0]
    
    member_count = team_info["COUNT(team_members.team_id)"]
    team_name = team_info["name"]

    # If the user is an admin, check if they are able to leave the team
    if privilege == "admin":
        if member_count == 1:
            return jsonify({"success": False, 
                            "error": "Admins cannot leave the team if they are the last member, please delete the team instead.", "name": team_name})
        
        admin_count = db.execute("SELECT COUNT(privilege) FROM team_members WHERE team_id = ? AND privilege = 'admin'", team_id)[0]["COUNT(privilege)"]
        if admin_count == 1:
            return jsonify({"success": False, 
                            "error": "Admins cannot leave the team if they are the last admin. Please delete the team, or pass on admin privileges instead.", "name": team_name})

    left_team_count = db.execute("DELETE FROM team_members WHERE team_id = ? AND user_id = ?", team_id, session["user_id"])
    if left_team_count == 0:
        return jsonify({"success": False})
    flash(f"Successfully left {team_name}")
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

    return jsonify({"status": "success"})
"""
Logic and route block end regarding board viewing and management.
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
