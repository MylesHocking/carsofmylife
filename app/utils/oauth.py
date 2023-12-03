"""from flask_dance.contrib.linkedin import make_linkedin_blueprint
from app.config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET
from flask_dance.consumer import oauth_authorized
from flask import flash


linkedin_blueprint = make_linkedin_blueprint(
    client_id=LINKEDIN_CLIENT_ID,
    client_secret=LINKEDIN_CLIENT_SECRET, 
    scope=[ "profile"],
    redirect_to="linkedin.authorized"  
)

# Connect to the signal for LinkedIn
@oauth_authorized.connect_via(linkedin_blueprint)
def linkedin_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with LinkedIn.", category="error")
        return False

    # The user was successfully authenticated with LinkedIn. 
    # You can now access user information with blueprint.session
    resp = blueprint.session.get("/v2/userinfo")
    print("resp is " + str(resp))
    # Do something with the response, like creating a user session.
    if resp.ok:
        user_info = resp.json()  # Parse the JSON response
        print(user_info)  # Output the user info to the console for debugging
        # Additional logic to handle user info (e.g., create user session, store data, etc.)
    else:
        print("Failed to fetch user information from LinkedIn.")

    return True  # Return False to prevent Flask-Dance from saving the token automatically if you want to handle token storage yourself.
"""