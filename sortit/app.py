# -*- coding: utf-8 -*-
from flask import Blueprint, url_for, render_template, jsonify, request, g, make_response, redirect, abort
from .utils import *
from .redis_functions import *
from .globals import *

sortit = Blueprint('sortit', __name__, template_folder='templates')

@sortit.route("/")
@sortit.route("/item/<item_id>")
@sortit.route("/item/<item_id>/room/<room_id>")
def render_item_room(item_id = "0", room_id = "root"):
    itemData = redis_get_all_view_information(item_id, g.uuid)
    if itemData[0] is None:
        abort(404)
    itemData[1] = itemData[1].decode('utf-8')

    #users personal ratings to lane on the right
    usersRatings = get_users_ratings(g.uuid, item_id, -1)
    numberOfUserRatings = len(usersRatings)
    numberOfShownRatings = numberOfUserRatings + 5 - numberOfUserRatings%5

    if room_id == "root":
        #averages to left lane
        leftLaneRatings = redis.zrevrange("item:"+item_id+":average", 0, numberOfShownRatings-1)
        numberOfElementsHidden = items_hidden("item:"+item_id+":average", numberOfShownRatings)
        leftLaneTitle = "Average sort"
        hideRoomGenerationLink = False
    else:
        # room owners ratings, showed in left lane
        roomOwner = redis.get("item:"+item_id+":"+room_id)
        leftLaneRatings = get_users_ratings(roomOwner, item_id, numberOfShownRatings-1)
        numberOfElementsHidden = items_hidden("user:"+roomOwner+":"+item_id, numberOfShownRatings)
        sortName = redis.get("user:"+roomOwner)
        if sortName is None:
            leftLaneTitle = "Anonymous sort"
        else:
            leftLaneTitle = sortName + "'s sort"
        hideRoomGenerationLink = True

    result = get_items(usersRatings)
    result2 = get_items(leftLaneRatings)
    resp = make_response(render_template('index.html',
            roomData = itemData,
            roomId = room_id,
            itemId = item_id,
            backgroundColor = lighten_color_and_return_hex(hex_to_rgb(itemData[2])),
            userRatings = result,
            averageRatings = result2,
            leftLaneTitle = leftLaneTitle,
            hideLink = hideRoomGenerationLink,
            numberOfElementsHidden = numberOfElementsHidden))
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

@sortit.route("/_add_item", methods=['POST'])
@sortit.route("/item/<item_id>/_add_item", methods=['POST'])
@sortit.route("/item/<item_id>/room/<room_id>/_add_item", methods=['POST'])
def add_item_for_user(room_id = "root", item_id = "0"):
    newItemID = request.form.get("item", "", type=str)
    if newItemID == "":
        #generate new item!
        newItemTitle = request.form.get("title").strip()
        print(newItemTitle)
        if newItemTitle == "":
            return jsonify(result = "error")
        newItemID = add_item(newItemTitle, item_id)[0]
    else:
        if redis.zrank('user:'+g.uuid+':'+item_id,newItemID):
            return jsonify(result = "error")
    usersRatings = redis.zrevrange('user:'+g.uuid+':'+item_id, 0, -1)
    usersRatings.append(newItemID)
    update_ratings(usersRatings, item_id, g.uuid)
    result = get_items([newItemID])
    return jsonify(result = result)

@sortit.route("/_update_order", methods=['POST'])
@sortit.route("/item/<item_id>/_update_order", methods=['POST'])
@sortit.route("/item/<item_id>/room/<room_id>/_update_order", methods=['POST'])
def update_order(room_id = "root", item_id = "0"):
    itemList = request.form.getlist("items[]")
    update_ratings(itemList, item_id, g.uuid)
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

@sortit.route("/_update_left_lane")
@sortit.route("/item/<item_id>/_update_left_lane")
@sortit.route("/item/<item_id>/room/<room_id>/_update_left_lane")
def update_left_lane(room_id="root", item_id="0"):
    numberOfItems = request.args.get("itemCount")
    if room_id != "root":
        #left lane is someones personal sort
        roomOwner = redis.get("item:"+item_id+":"+room_id)
        items = redis.zrevrange("user:"+roomOwner+":"+item_id, 0, int(numberOfItems)-1)
        itemsLeft = items_hidden("user:"+roomOwner+":"+item_id, numberOfItems)
    else:
        #left lane is average
        items = redis.zrevrange("item:"+item_id+":average", 0, int(numberOfItems)-1)
        itemsLeft = items_hidden("item:"+item_id+":average", numberOfItems)
    results = get_items(items)
    return jsonify(items = results, left = itemsLeft)


@sortit.route("/my_room")
@sortit.route("/item/<item_id>/my_room")
def redirect_to_my_room(item_id = "0"):
    room_id = redis.get('user:'+g.uuid+':'+item_id+":room")
    if room_id is None:
        room_id = new_room(item_id, g.uuid)
    return redirect(url_for('sortit.render_item_room', item_id=item_id, room_id=room_id), code=303)

@sortit.route("/item/<item_id>/vote/<attribute>")
def redirect_to_vote_item(item_id, attribute):
    global ALLOWED_ATTRIBUTES
    if not attribute in ALLOWED_ATTRIBUTES:
        abort(404)
    item = redis.hmget('item:'+ item_id, str(attribute)+'_id', attribute)
    child_item = item[0]
    if not child_item:
        pipe = redis.pipeline()
        child_item = add_item("Vote for item "+item_id+" "+attribute, -1, pipe)[0]
        add_connection_between_items(item_id, child_item, attribute, pipe)
        pipe.execute()
    return redirect(url_for('sortit.render_item_room', item_id=child_item), code=303)


@sortit.route("/_search_items")
@sortit.route("/item/<item_id>/_search_items")
@sortit.route("/item/<item_id>/room/<room_id>/_search_items")
def search_items(room_id = "root", item_id = "0"):
    string = request.args.get("search_string", "", type=str).lower()
    string = string.replace('*','')
    results = search_string(string, item_id)
    return jsonify(movies = results)

if __name__ == '__main__':
    app.debug = False
    load_lua_scripts()
    app.run()
