import flask
import importlib
import os

from flask_mobility import Mobility

app = flask.Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)
Mobility(app)

for route_file in os.listdir("routes"):
    if route_file.endswith(".py"):
        lib = importlib.import_module("routes." + route_file[:-3])
        app.register_blueprint(lib.blueprint)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)