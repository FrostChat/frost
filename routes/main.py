import binascii
import flask
import hashlib
import base64

from utils.sqlite import Database, UserNotFound

blueprint = flask.Blueprint('main', __name__, url_prefix='/')

@blueprint.route('/')
def index():
    if "user" in flask.session:
        return flask.redirect('/app')

    return flask.render_template('login.html')

@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.redirect('/')

    error = None
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")

    db = Database()
    user = None

    try:
        user = db.get_user_by_username(username)
    except UserNotFound:
        error = "A user with that username does not exist."

    if user:
        if hashlib.sha256(password.encode()).hexdigest() == user.hash:
            flask.session['user'] = {
                "username": user.username,
                "api_key": user.api_key
            }
            return flask.redirect("/app")
        else:
            error = "Username or password is incorrect"
    else:
        error = "A user with that username does not exist."
    
    return flask.render_template("login.html", error=error)

@blueprint.route("/logout")
def logout():
    flask.session.pop("user", None)
    return flask.redirect("/")