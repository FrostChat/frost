import flask

blueprint = flask.Blueprint("pwa", __name__)

@blueprint.route('/<path:path>')
def static_file(path):
    if path == 'manifest.json':
        return flask.send_from_directory('static', 'manifest.json')
    elif path == 'sw.js':
        response = flask.make_response(flask.send_from_directory('static/js', 'sw.js'))
        response.headers['Cache-Control'] = 'no-cache'
        return response
    else:
        return flask.jsonify({})