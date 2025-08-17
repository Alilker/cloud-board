import requests
import os

from flask import redirect, render_template, request, session, flash
from functools import wraps
import sqlite3

class Database:
    def __init__(self, database_path):
        self.database_path = database_path
    
    def execute(self, query, *args):
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, args)
            
            # Handle different query types
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]  # Convert to list of dicts
            elif query.strip().upper().startswith('INSERT'):
                conn.commit()
                result = cursor.lastrowid  # Return the ID of inserted row
            else:
                conn.commit()
                result = cursor.rowcount  # Return number of affected rows
                
            return result
        finally:
            conn.close()

database_path = os.path.join(os.path.dirname(__file__), "teampost.db")
db = Database(database_path)

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


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


def lookup(symbol):
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"