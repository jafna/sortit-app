# -*- coding: utf-8 -*-

from flask.ext.script import Manager

from sortit import create_app
from sortit.redis_functions import redis, make_base_structure
from sortit.globals import *

app = create_app()
manager = Manager(app)

@manager.command
def run():
    """Run in local machine."""
    app.run()

@manager.command
def init():
    """Reset+init database."""
    print("### Started to load initial data. ###")
    redis.flushall()
    make_base_structure()

if __name__ == "__main__":
    manager.run()
