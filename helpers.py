from flask import jsonify, render_template, request, session, flash
from functools import wraps
from cs50 import SQL


db = SQL("sqlite:///cloud-board.db")


# Adapted from the CS50 Finance's login_required decorator to require dynamic privileges
# Support for dynamic output types
def privilege_required(privilege, response_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            # Check if the inputted privilege is valid, simply for debugging purposes
            if privilege in ["login", "member", "editor", "admin"]:
                
                # Check for log in
                if session.get("user_id") is None:
                    if response_type == "json":
                        return jsonify({"success": False, 
                                        "error": "You must be logged in for this action!"})
                    flash("You must be logged in to access this page!")
                    return render_template("login.html")
                
                user_exists = db.execute("SELECT 1 FROM users WHERE id = ?", session["user_id"])

                # Ensure that user exists, if not clear their session and prompt for re-login
                if not user_exists:
                    session.clear()
                    if response_type == "json":
                        return jsonify({"success": False, 
                                        "error": "User for this action does not exist!"})
                    flash("User does not exist!")
                    return render_template("login.html")

                if privilege in ["member", "editor", "admin"]:
                    
                    # Check for membership
                    team_name = kwargs.get("team_name")
                    team = db.execute("SELECT * FROM teams WHERE name = ?", team_name)
                    
                    if not team:
                        if response_type == "json":
                            return jsonify({"success": False, 
                                            "error": "Requested team for this action does not exist!"})
                            
                        return render_template("error.html", error="Requested team does not exist!")

                    membership = db.execute(
                        "SELECT privilege FROM team_members WHERE team_id = ? AND user_id = ?",
                        team[0]["id"], session["user_id"])
                    
                    if not membership:
                        if response_type == "json":
                            return jsonify({"success": False, 
                                            "error": f"You must be a member of {team_name} for this action!"})
                            
                        return render_template("error.html", error=f"You must be a member of {team_name} to access this page!")

                    actual_privilege = membership[0]["privilege"]

                    # Check for required privilege
                    if privilege == "editor":
                        if actual_privilege not in ["editor", "admin"]:
                            if response_type == "json":
                                return jsonify({"success": False, 
                                                "error": "You do not have authorization for this action!"})
                                
                            return render_template("error.html", error="You do not have permission to view this page!")
                    
                    if privilege == "admin":
                        if actual_privilege != "admin":
                            if response_type == "json":
                                return jsonify({"success": False, 
                                                "error": "You do not have authorization for this action!"})
                                
                            return render_template("error.html", error="You do not have permission to view this page!")
            
            # Log incorrect privilege access
            else:
                print("Incorrect privilege!")
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
