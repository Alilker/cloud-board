from flask import jsonify, render_template, request, session, flash
from functools import wraps
from cs50 import SQL


db = SQL("sqlite:///teampost.db")


# Login required decorator that is from CS50's Finance problem set.
def login_required(f):
    """
    Decorate routes to require login

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to access this page!")
            return render_template("login.html", request_path=request.path)
        return f(*args, **kwargs)

    return decorated_function

# Adapted from the login_required decorator for API purposes
def api_login_required(f):
    """
    Decorate routes to require login for API endpoints

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return jsonify({"success": False, 
                            "error": "You must be logged in to access this page!"})
        return f(*args, **kwargs)

    return decorated_function


# Adapted from the login_required decorator to also require membership to the team
def membership_required(f):
    """
    Decorate route to require team membership
    """
    
    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to access this page!")
            return render_template("login.html")

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return render_template("error.html", error="Requested team does not exist!")

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"]
        )
        if not membership:
            return render_template("error.html", error=f"You must be a member of {team_name} to access this page!")
        return f(*args, **kwargs)
        
    return decorated_function

# Adapted from the membership_required for API purposes
def api_membership_required(f):
    """
    Decorate route to require team membership
    """
    
    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            return jsonify({"success": False, 
                            "error": "You must be logged in to access this page!"})

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return jsonify({"success": False, 
                            "error": "Requested team does not exist!"})

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"]
        )
        if not membership:
            return jsonify({"success": False, 
                            "error": f"You must be a member of {team_name} to access this page!"})
        return f(*args, **kwargs)
        
    return decorated_function


# Adapted from the login_required decorator to also require editor privileges
def edit_required(f):
    """
    Decorate route to require editor privileges
    """

    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to access this page!")
            return render_template("login.html")

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return render_template("error.html", error="Requested team does not exist!")

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"])[0]
        
        if not membership:
            return render_template("error.html", error=f"You must be a member of {team_name} to access this page!")

        privilege = membership["privilege"]
        if privilege not in ["editor", "admin"]:
            return render_template("error.html", error="You do not have permission to view this page!")
        return f(*args, **kwargs)
    return decorated_function

# Adapted from the edit_required for API purposes
def api_edit_required(f):
    """
    Decorate route to require editor privileges for API endpoints
    """

    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            return jsonify({"success": False, 
                            "error": "You must be logged in to access this page!"})

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return jsonify({"success": False, 
                            "error": "Requested team does not exist!"})

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"])[0]
        
        if not membership:
            return jsonify({"success": False, 
                            "error": f"You must be a member of {team_name} to access this page!"})

        privilege = membership["privilege"]
        if privilege not in ["editor", "admin"]:
            return jsonify({"success": False, 
                            "error": "You do not have permission to view this page!"})
        return f(*args, **kwargs)
    return decorated_function


# Adapted from the login_required decorator to also require admin privileges
def admin_required(f):
    """
    Decorate route to require admin privileges
    """

    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to access this page!")
            return render_template("login.html")

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return render_template("error.html", error="Requested team does not exist!")

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"])[0]
        
        if not membership:
            return render_template("error.html", error=f"You must be a member of {team_name} to access this page!")

        privilege = membership["privilege"]
        if privilege != "admin":
            return render_template("error.html", error="You do not have permission to view this page!")
        return f(*args, **kwargs)
    return decorated_function

# Adapted from the admin_required decorator for API purposes
def api_admin_required(f):
    """
    Decorate route to require admin privileges for API endpoints
    """

    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            return jsonify({"success": False, 
                            "error": "You must be logged in to access this page!"})

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return jsonify({"success": False, 
                            "error": "Requested team does not exist!"})

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"])[0]
        
        if not membership:
            return jsonify({"success": False, 
                            "error": f"You must be a member of {team_name} to access this page!"})

        privilege = membership["privilege"]
        if privilege != "admin":
            return jsonify({"success": False, 
                            "error": "You do not have permission to view this page!"})
        return f(*args, **kwargs)
    return decorated_function
