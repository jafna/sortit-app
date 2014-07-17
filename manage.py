# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from sortit import create_app
from sortit.redis_functions import redis
from gevent.wsgi import WSGIServer

import werkzeug.serving
import sortit.globals

app = create_app()
manager = Manager(app)

@manager.command
@werkzeug.serving.run_with_reloader
def debug():
    app.debug = True
    server = WSGIServer(("", 5000), app)
    server.serve_forever()

@manager.command
def run():
    app.debug = False
    server = WSGIServer(("", 5000), app)
    server.serve_forever()

if __name__ == "__main__":
    manager.run()
