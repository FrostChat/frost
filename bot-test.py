import socketio
import shlex

class Message:
    def __init__(self, id, content, author_id, timestamp):
        self.id = id
        self.content = content
        self.author_id = author_id
        self.timestamp = timestamp

class Bot:
    def __init__(self):
        self.sio = socketio.Client()

    def run(self, api_key: str):
        self.sio.connect('http://localhost:8080', transports=["websocket"])
        self.sio.emit("authenticate", {"api_key": "Ym90.U3h2aHpnbFNzZUVrbW93WQ=="})

    def event(self, *args):
        event_name = args[0].__name__
        event_callback = args[0]

        self.sio.on(event_name, event_callback)

frost_bot = Bot()

@frost_bot.event
def authenticated(data):
    print("Connected to Frost")

@frost_bot.event
def message(data):
    msg = Message(data["id"], data["content"], data["author_id"], data["timestamp"])

    if msg.content.startswith("/"):
        cmd = msg.content[1:]
        args = shlex.split(cmd)

        if args[0] == "ping":
            frost_bot.sio.emit("send_message", {"content": "pong", "receiver_id": msg.author_id})

        if args[0] == "help":
            help_message = """**📖 Commands**
/ping - Pong
/help - This message
/info - Get info about Frost
/userinfo [user_id] - Get info about a user
/messageinfo [message_id] - Get info about a message
"""
            frost_bot.sio.emit("send_message", {"content": help_message, "receiver_id": msg.author_id})

frost_bot.run("Qm9i.WllkdTdqWWtSMnpPUjVkRw==")