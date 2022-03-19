import flask
import hashlib

from utils.sqlite import Database, InvalidBio, UserNotFound, UserMuted, UserNotMuted, UserBlocked, UserNotBlocked

blueprint = flask.Blueprint('api', __name__, url_prefix='/api')

# @blueprint.route("/change_username", methods=['GET', 'POST'])
# def change_username():
#     if flask.request.method == 'GET':
#         return flask.redirect(flask.request.referrer)
    
#     db = Database()
#     if "user" not in flask.session:
#         return flask.jsonify({"error": "Not logged in"})

#     user = db.get_user_by_username(flask.session['user']['username'])
#     if not user:
#         return flask.jsonify({"error": "User not found"})

#     new_username = flask.request.form.get('username')
#     password = flask.request.form.get('password')
#     hashed_password = hashlib.sha256(password.encode()).hexdigest()

#     if hashed_password != user.hash:
#         return flask.jsonify({"error": "Password is incorrect"})

#     if db.get_user_by_username(new_username):
#         return flask.jsonify({"error": "Username already taken"})
        
#     db.change_user_username(new_username, user.id)
#     flask.session.pop('user', None)
   
#     if "/app" in flask.request.referrer:
#         return flask.redirect(flask.request.referrer)

#     return flask.jsonify({"success": "Username changed"})

@blueprint.get('/user/<user_id>')
def get_user(user_id):
    api_key = flask.request.headers.get('Authorization')
    db = Database()

    if not db.valid_api_key(api_key):
        return flask.jsonify({'error': 'Invalid API key.'}), 403

    if user_id == "@me":
        try:
            user_id = api_key.split('.')[0]
        except UserNotFound:
            return flask.jsonify({'error': 'User not found.'}), 404
    
    user = None
    api_key_user = None
    
    try:
        user = db.get_user(user_id)
    except UserNotFound:
        return flask.jsonify({'error': 'User not found.'}), 404
    if not user:
        return flask.jsonify({'error': 'User not found.'}), 404

    try:
        api_key_user = db.get_user(api_key.split('.')[0])
    except UserNotFound:
        return flask.jsonify({'error': 'Invalid API key.'}), 404
    if api_key_user.id != user.id:
        is_user_muted = db.is_user_muted(api_key_user.id, user.id)
        user.is_muted = is_user_muted

    return flask.jsonify(user.to_json())

@blueprint.patch('/user/<user_id>')
def update_user(user_id):
    api_key = flask.request.headers.get('Authorization')
    api_user_id = api_key.split('.')[0]
    db = Database()

    if not db.valid_api_key(api_key):
        return flask.jsonify({'error': 'Invalid API key.'}), 403

    if user_id == "@me":
        try:
            user_id = api_key.split('.')[0]
        except UserNotFound:
            return flask.jsonify({'error': 'User not found.'}), 404
    
    user = db.get_user(user_id)
    if not user:
        return flask.jsonify({'error': 'User not found.'}), 404

    if api_user_id == user.id:
        data = flask.request.get_json()

        if 'avatar_url' in data:
            db.change_user_avatar_url(data['avatar_url'], user.id)
        
        if 'website' in data:
            db.change_user_website(data['website'], user.id)

        if 'bio' in data:
            try:
                db.change_user_bio(data['bio'], user.id)
            except InvalidBio:
                return flask.jsonify({'error': 'Bio is greater than 200 characters.'}), 400

        return flask.jsonify({'success': 'Updated your profile.'}), 200

    return flask.jsonify({'error': 'You do not have permission to update this user.'}), 403

# @blueprint.route('/user/<user_id>', methods=["GET", "PATCH"])
# def get_user(user_id):
#     api_key = flask.request.headers.get('Authorization')
#     db = Database()

#     if not db.valid_api_key(api_key):
#         return flask.jsonify({'error': 'Invalid API key.'}), 403

#     if user_id == "@me":
#         try:
#             user_id = api_key.split('.')[0]
#         except UserNotFound:
#             return flask.jsonify({'error': 'User not found.'}), 404
    
#     user = db.get_user(user_id)
#     if not user:
#         return flask.jsonify({'error': 'User not found.'}), 404

#     api_key_user = db.api_key_to_user(api_key)
#     if api_key_user.id != user.id:
#         is_user_muted = db.is_user_muted(api_key_user.id, user.id)
#         user.is_muted = is_user_muted

#     if flask.request.method == "GET":
#         return flask.jsonify(user.to_json())

#     elif flask.request.method == "PATCH":
#         data = flask.request.get_json()

#         if user.id != api_key_user.id:
#             return flask.jsonify({'error': 'You can only update your own profile.'}), 403

#         else:
#             if 'avatar_url' in data:
#                 db.change_user_avatar_url(data['avatar_url'], user.id)
#                 return flask.jsonify({'success': 'Avatar URL changed.'})
            
#             if 'website' in data:
#                 db.change_user_website(data['website'], user.id)
#                 return flask.jsonify({'success': 'Website changed.'})

#             if 'bio' in data:
#                 try:
#                     db.change_user_bio(data['bio'], user.id)
#                     return flask.jsonify({'success': 'Bio changed.'})
#                 except InvalidBio:
#                     return flask.jsonify({'error': 'Bio is greater than 200 characters.'}), 400

@blueprint.post("/user/<user_id>/mute")
def mute_user(user_id):
    api_key = flask.request.headers.get('Authorization')
    api_user_id = api_key.split('.')[0]
    db = Database()

    if not db.valid_api_key(api_key):
        return flask.jsonify({'error': 'Invalid API key.'}), 403

    if user_id == api_user_id:
        return flask.jsonify({'error': 'You cannot mute yourself.'}), 403

    user = db.get_user(user_id)
    if not user:
        return flask.jsonify({'error': 'User not found.'}), 404

    if db.is_user_muted(api_user_id, user.id):
        return flask.jsonify({'error': 'User is already muted.'}), 400
    
    try:
        db.mute_user(api_user_id, user.id)
    except UserMuted:
        return flask.jsonify({'error': 'User is already muted.'}), 400

    return flask.jsonify({'success': 'User muted.'})

@blueprint.post("/user/<user_id>/unmute")
def unmute_user(user_id):
    api_key = flask.request.headers.get('Authorization')
    api_user_id = api_key.split('.')[0]
    db = Database()

    if not db.valid_api_key(api_key):
        return flask.jsonify({'error': 'Invalid API key.'}), 403

    if user_id == api_user_id:
        return flask.jsonify({'error': 'You cannot mute yourself.'}), 403

    user = db.get_user(user_id)
    if not user:
        return flask.jsonify({'error': 'User not found.'}), 404

    if not db.is_user_muted(api_user_id, user.id):
        return flask.jsonify({'error': 'User is not muted.'}), 400

    try:
        db.unmute_user(api_user_id, user.id)
    except UserNotMuted:
        return flask.jsonify({'error': 'User is not muted.'}), 400

    return flask.jsonify({'success': 'User unmuted.'})

@blueprint.post("/user/<user_id>/block")
def block_user(user_id):
    api_key = flask.request.headers.get('Authorization')
    api_user_id = api_key.split('.')[0]
    db = Database()

    if not db.valid_api_key(api_key):
        return flask.jsonify({'error': 'Invalid API key.'}), 403

    if user_id == api_user_id:
        return flask.jsonify({'error': 'You cannot block yourself.'}), 403

    user = db.get_user(user_id)
    if not user:
        return flask.jsonify({'error': 'User not found.'}), 404

    if db.is_user_blocked(api_user_id, user.id):
        return flask.jsonify({'error': 'User is already blocked.'}), 400

    try:
        db.block_user(api_user_id, user.id)
    except UserBlocked:
        return flask.jsonify({'error': 'User is already blocked.'}), 400

    return flask.jsonify({'success': 'User blocked.'})

@blueprint.post("/user/<user_id>/unblock")
def unblock_user(user_id):
    api_key = flask.request.headers.get('Authorization')
    api_user_id = api_key.split('.')[0]
    db = Database()

    if not db.valid_api_key(api_key):
        return flask.jsonify({'error': 'Invalid API key.'}), 403

    if user_id == api_user_id:
        return flask.jsonify({'error': 'You cannot block yourself.'}), 403

    user = db.get_user(user_id)
    if not user:
        return flask.jsonify({'error': 'User not found.'}), 404

    if not db.is_user_blocked(api_user_id, user.id):
        return flask.jsonify({'error': 'User is not blocked.'}), 400

    try:
        db.unblock_user(api_user_id, user.id)
    except UserNotBlocked:
        return flask.jsonify({'error': 'User is not blocked.'}), 400

    return flask.jsonify({'success': 'User unblocked.'})

# @blueprint.route('/user/<user_id>/messages')
# def get_messages(user_id):
#     api_key = flask.request.headers.get('Authorization')
#     db = Database()

#     if not db.valid_api_key(api_key):
#         return flask.jsonify({'error': 'Invalid API key.'}), 403

#     api_user = api_key.split('.')[0]
#     messages = db.get_messages_between(api_user, user_id)

#     return flask.jsonify([message.to_json() for message in messages])

# @blueprint.route('/user/<user_id>/messages', methods=['PUT'])
# def send_message(user_id):
#     api_key = flask.request.headers.get('Authorization')
#     db = Database()

#     if not db.valid_api_key(api_key):
#         return flask.jsonify({'error': 'Invalid API key.'}), 403

#     api_user = api_key.split('.')[0]
#     body = flask.request.get_json()

#     print(api_user)

#     if not body:
#         return flask.jsonify({'error': 'Missing body.'}), 400

#     if 'content' not in body:
#         return flask.jsonify({'error': 'Missing content.'}), 400
    
#     new_msg = db.add_message(body['content'], api_user, user_id)
#     messages = db.get_messages_between(api_user, user_id)
    
#     return flask.jsonify([message.to_json() for message in messages])

@blueprint.route('/message/<message_id>')
def get_message(message_id):
    api_key = flask.request.headers.get('Authorization')
    db = Database()

    if not db.valid_api_key(api_key):
        return flask.jsonify({'error': 'Invalid API key.'}), 403

    if not db.get_message(message_id):
        return flask.jsonify({'error': 'Message not found.'}), 404

    message = db.get_message(message_id)
    return flask.jsonify(message.to_json())

# @blueprint.route('/message/<message_id>', methods=['PATCH'])
# def edit_message(message_id):
#     api_key = flask.request.headers.get('Authorization')
#     db = Database()

#     if not db.valid_api_key(api_key):
#         return flask.jsonify({'error': 'Invalid API key.'}), 403

#     if not db.get_message(message_id):
#         return flask.jsonify({'error': 'Message not found.'}), 404

#     message = db.get_message(message_id)
#     split_api_key = api_key.split('.')

#     if message.author_id != split_api_key[0]:
#         return flask.jsonify({'error': 'You are not the author of this message.'}), 403

#     body = flask.request.get_json()
#     content = body.get('content')

#     if not content:
#         return flask.jsonify({'error': 'Missing content.'}), 400

#     edited_msg = db.edit_message(message_id, content)
#     return flask.jsonify(edited_msg.to_json())

# @blueprint.route('/message/<message_id>', methods=['DELETE'])
# def delete_message(message_id):
#     api_key = flask.request.headers.get('Authorization')
#     db = Database()

#     if not db.valid_api_key(api_key):
#         return flask.jsonify({'error': 'Invalid API key.'}), 403

#     if not db.get_message(message_id):
#         return flask.jsonify({'error': 'Message not found.'}), 404

#     message = db.get_message(message_id)
#     split_api_key = api_key.split('.')

#     if message.author_id != split_api_key[0]:
#         return flask.jsonify({'error': 'You are not the author of this message.'}), 403

#     db.delete_message(message_id)
#     return flask.jsonify({'success': 'Message deleted.'}), 200