import binascii
import flask
import hashlib
import base64

from utils.sqlite import Database, UserNotFound

blueprint = flask.Blueprint('app', __name__, url_prefix='/app')

@blueprint.route("/")
def index():
    db = Database()
    if 'user' not in flask.session:
        return flask.redirect("/")
        
    self_user = db.get_user_by_username(flask.session['user']['username'])
    users = db.get_users_chats(self_user.id)

    for user in users:
        is_muted = db.is_user_muted(self_user.id, user.id)
        user.is_muted = is_muted

    users_json = [user.to_json() for user in users]

    return flask.render_template('app/app.html', users=users, users_json=users_json, self_user=self_user)

@blueprint.route('/chat/<user_id>')
def chat(user_id):
    db = Database()
    if 'user' not in flask.session:
        return flask.redirect("/")

    user = None
    try:
        test = base64.b64decode(user_id).decode()
        user = db.get_user(user_id)
    except binascii.Error:
        try:
            user = db.get_user_by_username(user_id)
        except UserNotFound:
            return flask.redirect("/app")
        if user:
            return flask.redirect(f"/app/chat/{user.id}")
        else:
            return flask.redirect("/app")
    except Exception as e:
        print(e)
        return flask.redirect("/app")

    self_user = db.get_user_by_username(flask.session['user']['username'])
    users = db.get_users_chats(self_user.id)

    for user in users:
        is_muted = db.is_user_muted(self_user.id, user.id)
        user.is_muted = is_muted

    users_json = [user.to_json() for user in users]
    messages = db.get_messages_between(self_user.id, user.id)

    return flask.render_template('app/chat.html', users=users, user=user, users_json=users_json, messages=messages, messages_json=[ msg.to_json() for msg in messages ], self_user=self_user)

@blueprint.route("/mobile-settings")
def mobile_settings():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])

    return flask.render_template("/app/settings/mobile-settings.html", self_user=self_user)

@blueprint.route("/settings")
def settings():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])

    if flask.request.MOBILE:
        return flask.render_template("/app/settings/mobile-settings.html", self_user=self_user, request=flask.request)

    return flask.redirect(flask.url_for(".settings_account"))

@blueprint.route("/settings/account")
def settings_account():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])

    return flask.render_template('app/settings/account.html', self_user=self_user, request=flask.request)

@blueprint.route("/settings/profile")
def settings_profile():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])

    return flask.render_template('app/settings/profile.html', self_user=self_user, request=flask.request)