# -*- coding: utf-8 -*-
import os

def init():
    global PROJECT_ROOT
    global DEFAULT_BLUEPRINTS
    global REDIS_LUA_SEARCH_ITEM
    global REDIS_LUA_CALCULATE_AVERAGE_ORDER

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

