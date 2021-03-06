import binascii
import flask
import hashlib
import base64

from psutil import users

from utils.sqlite import Database, UserNotFound

blueprint = flask.Blueprint('app', __name__, url_prefix='/app')

@blueprint.route("/")
def index():
    db = Database()
    if 'user' not in flask.session:
        return flask.redirect("/")
        
    self_user = db.get_user_by_username(flask.session['user']['username'])
    users = db.get_users_chats(self_user.id)
    theme = db.get_theme(self_user.id)

    for user in users:
        is_muted = db.is_user_muted(self_user.id, user.id)
        is_blocked = db.is_user_blocked(self_user.id, user.id)

        user.is_muted = is_muted
        user.is_blocked = is_blocked

    users_json = [user.to_json() for user in users]

    return flask.render_template('app/app.html', users=users, users_json=users_json, self_user=self_user, theme=theme)

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
    theme = db.get_theme(self_user.id)

    for user2 in users:
        is_muted = db.is_user_muted(self_user.id, user2.id)
        is_blocked = db.is_user_blocked(self_user.id, user2.id)

        user2.is_muted = is_muted
        user2.is_blocked = is_blocked

    user.is_blocked = db.is_user_blocked(self_user.id, user.id)
    user.is_muted = db.is_user_muted(self_user.id, user.id)

    users_json = [user.to_json() for user in users]
    messages = db.get_messages_between(self_user.id, user.id)

    return flask.render_template('app/chat.html', users=users, user=user, users_json=users_json, messages=messages, messages_json=[ msg.to_json() for msg in messages ], self_user=self_user, theme=theme)

@blueprint.route("/mobile-settings")
def mobile_settings():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])
    theme = db.get_theme(self_user.id)

    return flask.render_template("/app/settings/mobile-settings.html", self_user=self_user, theme=theme)

@blueprint.route("/settings")
def settings():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])
    theme = db.get_theme(self_user.id)

    if flask.request.MOBILE:
        return flask.render_template("/app/settings/mobile-settings.html", self_user=self_user, request=flask.request, theme=theme)

    return flask.redirect(flask.url_for(".settings_account"))

@blueprint.route("/settings/account")
def settings_account():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])
    blocked_users = [user.to_json() for user in db.get_blocked_users(self_user.id)]
    users_json = [user.to_json() for user in db.get_users_chats(self_user.id)]
    theme = db.get_theme(self_user.id)

    return flask.render_template('app/settings/account.html', self_user=self_user, blocked_users=blocked_users, users_json=users_json, request=flask.request, theme=theme)

@blueprint.route("/settings/profile")
def settings_profile():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])
    theme = db.get_theme(self_user.id)

    return flask.render_template('app/settings/profile.html', self_user=self_user, request=flask.request, theme=theme)

@blueprint.route("/settings/appearance")
def settings_appearance():
    db = Database()

    if 'user' not in flask.session:
        return flask.redirect("/")
    
    self_user = db.get_user_by_username(flask.session['user']['username'])
    theme = db.get_theme(self_user.id)

    return flask.render_template('app/settings/appearance.html', self_user=self_user, request=flask.request, theme=theme)