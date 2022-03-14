import socketio

sio = socketio.Client()
sio.connect('http://0.0.0.0:5000')
sio.emit('authenticate', {"api_key": "QmVubnk=.R1B6a3ZSUFIyMDhTOGFDVQ=="})

@sio.on('authenticated')
def authenticated(data):
    print(data)

@sio.on('disconnect')
def on_disconnect():
    print('disconnected from server')

@sio.on("message")
def on_message(data):
    print(data)