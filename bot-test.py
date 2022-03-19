import socketio

sio = socketio.Client()
sio.connect("http://localhost:8080", transports=["websocket"])
sio.emit("authenticate", {"api_key": "Ym90.U3h2aHpnbFNzZUVrbW93WQ=="})

@sio.on('authenticated')
def authenticated(data):
    print("connected")

@sio.on('message')
def message(data):
    content = data.get("content")
    author_id = data.get("author_id")

    if content.startswith("!"):
        command = content.replace("!", "").split(" ")
        if command[0] == "ping":
            sio.emit("send_message", {"content": """asdasd
            asdad
            asd
            asdasd
            """, "receiver_id": author_id})