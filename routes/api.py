import flask
import hashlib

from utils.sqlite import Database, InvalidBio, UserNotFound

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

@blueprint.route('/user/<user_id>', methods=["GET", "PATCH"])
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
    
    user = db.get_user(user_id)
    if not user:
        return flask.jsonify({'error': 'User not found.'}), 404

    if flask.request.method == "GET":
        return flask.jsonify(user.to_json())

    elif flask.request.method == "PATCH":
        data = flask.request.get_json()

        if 'avatar_url' in data:
            db.change_user_avatar_url(data['avatar_url'], user.id)
            return flask.jsonify({'success': 'Avatar URL changed.'})
        
        if 'website' in data:
            db.change_user_website(data['website'], user.id)
            return flask.jsonify({'success': 'Website changed.'})

        if 'bio' in data:
            try:
                db.change_user_bio(data['bio'], user.id)
                return flask.jsonify({'success': 'Bio changed.'})
            except InvalidBio:
                return flask.jsonify({'error': 'Bio is greater than 200 characters.'}), 400

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