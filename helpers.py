from flask import render_template, request, session, flash
from functools import wraps
from cs50 import SQL
db = SQL("sqlite:///finance.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to access this page.")
            return render_template("login.html", request_path=request.path)
        return f(*args, **kwargs)

    return decorated_function

def membership_required(f):
    """
    Decorate route to require team membership
    """
    
    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to view and/or make changes to this team.")
            return render_template("login.html")

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return render_template("error.html", error="Team doesn't exist")

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"]
        )
        if not membership:
            return render_template("error.html", error="You are not a member of this team")
        return f(*args, **kwargs)
        
    return decorated_function

def admin_required(f):
    """
    Decorate route to require admin privileges
    """

    @wraps(f)
    def decorated_function(* args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to view and/or make changes to this team.")
            return render_template("login.html")

        team_name = kwargs.get("team_name")
        team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
        if not team:
            return render_template("error.html", error="Team doesn't exist")

        membership = db.execute(
            "SELECT * FROM team_members WHERE team_id = ? AND user_id = ?",
            team[0]["id"], session["user_id"])[0]
        
        if not membership:
            return render_template("error.html", error="You are not a member of this team")

        privilege = membership["privilege"]
        if privilege != "admin":
            return render_template("error.html", error="You do not have permission to view this page")
        return f(*args, **kwargs)
    return decorated_function
