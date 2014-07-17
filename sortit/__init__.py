# -*- coding: utf-8 -*-
from uuid import uuid4
from flask import Flask, g, session, Response
from .redis_functions import redis, load_lua_scripts
from .app import sortit

import globals

# Making it easy to add deferred request callbacks
def after_this_request(f):
    if not hasattr(g, "after_request_callbacks"):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f

def register_extensions(app):
    redis.init_app(app)

def register_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def create_app():
    globals.init()
    globals.DEFAULT_BLUEPRINTS = [sortit]

    app = Flask(__name__)
    app.config['REDIS_HOST'] = 'localhost'
    app.config['REDIS_PORT'] = 6379
    app.config['REDIS_DB'] = 0
    app.config['REDIS_CHARSET'] = 'utf-8'
    app.secret_key = 'put your own secret here'
    app.config.update(
        DEBUG=True,
        SECRET_KEY='Change this!'
    )

    register_extensions(app)
    register_blueprints(app, globals.DEFAULT_BLUEPRINTS)
    load_lua_scripts()

    @app.after_request
    def call_after_request_callbacks(response):
        for callback in getattr(g, "after_request_callbacks", ()):
            callback(response)
        return response

    # Userid automatically to every request
    @app.before_request
    def set_user_id():
        if 'uuid' in session:
            uuid = session['uuid']
            nick = session['nick']
        else:
            uuid = str(uuid4())
            nick = "Anonymous"+str(uuid4())[:3]
            redis.set("user:"+uuid, nick)
            @after_this_request
            def set_user_id(response):
                session['uuid'] = uuid
                session['nick'] = nick
        g.uuid = uuid
        g.nick = nick
    return app
