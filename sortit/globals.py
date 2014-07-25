# -*- coding: utf-8 -*-
import os

def init():
    global PROJECT_ROOT
    global MAX_ITEMS_IN_ONE_SORT
    global DEFAULT_BLUEPRINTS
    global REDIS_LUA_SEARCH_ITEM
    global REDIS_LUA_CALCULATE_AVERAGE_ORDER

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    MAX_ITEMS_IN_ONE_SORT = 5
