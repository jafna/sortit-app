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
    return make_response(render_template('angular-index.html'))

@sortit.route('/stream')
def stream():
    tags = request.args.getlist('tags')
    tags.sort()
    return Response(event_stream(['userchannel:'+g.uuid, 'tagchannel:'+'+'.join(tags)]), mimetype="text/event-stream")

@sortit.route("/_add_item", methods=['POST'])
def add_existing_item_for_user():
    postData = request.get_json()
    tags = postData["tags"]
    itemString = postData["item"]
    itemIds = add_item_for_user('item:'+itemString, tags, g.uuid)
    items = get_items(itemIds)
    return jsonify(items = items, state='ready')

@sortit.route("/_add_url", methods=['POST'])
def add_new_item_for_user():
    postData = request.get_json()
    tags = postData["tags"]
    url = postData["url"]
    if re.match('(?:http|ftp|https)://', url):
        if(fetch_url(url, tags, g.uuid)):
            return jsonify(state='resolving')
        return jsonify(state='error')

@sortit.route("/_update_order", methods=['POST'])
def update_order(room_id = "root", item_id = "0"):
    jsonData = request.get_json()
    items = jsonData['items']
    tags = jsonData['tags']
    items = ['item:'+s  for s in items]
    update_ratings(items, tags, g.uuid)
    return jsonify(items = "success")

@sortit.route("/_show_more_items")
@sortit.route("/item/<item_id>/_show_more_items")
@sortit.route("/item/<item_id>/room/<room_id>/_show_more_items")
def show_more_items(room_id = "root", item_id = "0"):
    numberOfItems = request.args.get("elements")
    numberOfItemsAfterFetch = int(numberOfItems)+10
    if room_id == "root":
        items = redis.zrevrange("item:"+item_id+":average", numberOfItems, numberOfItemsAfterFetch-1)
        itemsLeft = items_hidden("item:"+item_id+":average", numberOfItemsAfterFetch)
    else:
        roomOwner = redis.get("item:"+item_id+":"+room_id)
        items = redis.zrevrange("user:"+roomOwner+":"+item_id, numberOfItems, numberOfItemsAfterFetch-1)
        itemsLeft = items_hidden("user:"+roomOwner+":"+item_id, numberOfItemsAfterFetch)
    if items is None:
        return jsonify(items = "error")
    results = get_items(items)
    return jsonify(items = results, left = itemsLeft)

@sortit.route("/_get_average_items")
def get_average_items():
    tags = request.args.getlist('tags')
    averageRatings = get_average_ratings(tags)
    results = get_items(averageRatings)
    return jsonify(items = results)

@sortit.route("/_get_user_items")
def get_user_items():
    tags = request.args.getlist('tags')
    usersRatings = get_users_ratings(g.uuid, tags)
    results = get_items(usersRatings)
    return jsonify(items = results)

@sortit.route("/_search_items")
def search_items():
    string = request.args.get("searchString", "", type=str).lower()
    string = string.replace('*','')
    results = search_string(string)
    return jsonify(results = results)
