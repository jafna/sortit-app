# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

import re
from flask import Blueprint, url_for, render_template, jsonify, request, g, make_response, redirect, abort, Response
from .utils import *
from .redis_functions import *
from .globals import *
import ServerSentEvent

sortit = Blueprint('sortit', __name__, template_folder='templates')

@sortit.route('/')
@sortit.route('/<path:path>')
def render_item_room(path = ''):
    return make_response(render_template('index.html'))

@sortit.route('/stream')
def stream():
    tags = request.args.getlist('tags')
    tags.sort()
    tagsStr = '+'.join(tags)
    print 'user_channel:'+g.uuid+':tags:'+tagsStr
    return Response(event_stream(['user_channel:'+g.uuid+':tags:'+tagsStr,
        'tagchannel:'+tagsStr]), mimetype="text/event-stream")

def add_item_for_user_and_return_json(user, tags, itemTitle):
    itemIds = add_item_for_user('item:'+itemTitle, tags, user)
    items = get_items(itemIds)
    return jsonify(items = items, state="success")

@sortit.route("/_add_item", methods=['POST'])
def add_existing_item_for_user():
    postData = request.get_json()
    tags = postData["tags"]
    itemTitle = postData["item"]
    return add_item_for_user_and_return_json(g.uuid, tags, itemTitle)

@sortit.route("/_add_url", methods=['POST'])
def add_new_item_for_user():
    postData = request.get_json()
    tags = postData["tags"]
    url = postData["url"]
    if re.match('(?:http|ftp|https)://', url):
        itemTitle = fetch_url(url, tags, g.uuid, tags)
        if itemTitle:
            return add_item_for_user_and_return_json(g.uuid, tags,
                    itemTitle)
        else:
            return jsonify(state='resolving')
    return jsonify(state='error')

@sortit.route("/_update_order", methods=['POST'])
def update_order(room_id = "root", item_id = "0"):
    jsonData = request.get_json()
    items = jsonData['items']
    tags = jsonData['tags']
    items = ['item:'+s  for s in items]
    update_ratings(items, tags, g.uuid)
    return jsonify(state = "success")

@sortit.route("/_get_average_items")
def get_average_items():
    tags = request.args.getlist('tags')
    averageRatings = get_average_ratings(tags)
    results = get_items(averageRatings)
    return jsonify(items = results, state="success")

@sortit.route("/_get_user_items")
def get_user_items():
    tags = request.args.getlist('tags')
    usersRatings = get_users_ratings(g.uuid, tags)
    results = get_items(usersRatings)
    return jsonify(items = results, state="success")

@sortit.route("/_get_active_channels")
def get_active_channels():
    tags = request.args.getlist('tags')
    active_channels = get_activity(tags, 3)
    results = []
    for string in active_channels:
        categories = string.split("+")
        avg = get_average_ratings(categories, 2)
        results.append({'tags':categories, 'items':get_items(avg)})
    return jsonify(channels = results, state="success")

@sortit.route("/_search_items")
def search_items():
    string = request.args.get("searchString", "", type=str).lower()
    string = string.replace('*','')
    results = search_string(string)
    return jsonify(results = results)
