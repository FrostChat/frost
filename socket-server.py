import eventlet
import socketio
import datetime

from utils.sqlite import Database
from utils.emojis import shortname_to_emoji, emoji_shortnames

db = Database()
sio = socketio.Server(cors_allowed_origins="*", transports=["polling", "websocket", "xhr-polling", "jsonp-polling"])
app = socketio.WSGIApp(sio)
clients = {}

def get_sid_from_user_id(user_id: str) -> str:
    for key, value in clients.items():
        for k, v in value.items():
            if k == "user_id" and v == user_id:
                return key

    return None

@sio.on('connect')
def connect(sid, environ):
    pass

@sio.on('disconnect')
def disconnect(sid):
    if sid in clients:
        del clients[sid]

@sio.on('authenticate')
def authenticate(sid, data):
    api_key = data["api_key"]
    api_user_id = api_key.split(".")[0]

    clients[sid] = {
        "api_key": api_key,
        "user_id": api_user_id
    }

    if not db.valid_api_key(api_key):
        sio.disconnect(sid)

    sio.emit("authenticated", {"user_id": api_user_id}, room=sid)

@sio.on('send_message')
def send_message(sid, data):
    api_key = clients[sid]["api_key"]
    api_user_id = api_key.split(".")[0]

    content = data.get("content")
    receiver_id = data.get("receiver_id")

    content = content.replace('"', '')
    content = content.replace("'", "")

    # for shortname in emoji_shortnames:
    #     content = content.replace(shortname, shortname_to_emoji(shortname))

    if content is None or len(content) == 0:
        return

    message = db.add_message(content, api_user_id, receiver_id, str(datetime.datetime.now()))
    reciever_sid = get_sid_from_user_id(receiver_id)

    if reciever_sid is not None:
        sio.emit("message", message.to_json(), room=reciever_sid)

    sio.emit("message", message.to_json(), room=sid)

@sio.on('delete_message')
def delete_message(sid, data):
    api_key = clients[sid]["api_key"]
    api_user_id = api_key.split(".")[0]

    receiver_id = data.get("receiver_id")
    message_id = data.get("message_id")
    message_div_index = data.get("message_div_index")
    reciever_sid = get_sid_from_user_id(receiver_id)

    message = db.get_message(message_id)
    if message is None:
        return
    
    if message.author_id != api_user_id:
        return

    db.delete_message(message_id)
    sio.emit("message_deleted", {"message_div_index": message_div_index}, room=sid)

    if reciever_sid is not None:
        sio.emit("message_deleted", {"message_div_index": message_div_index}, room=reciever_sid)


@sio.on('message')
def message(sid, data):
    pass

@sio.on("message_deleted")
def message_deleted(sid, data):
    pass

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)