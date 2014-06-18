# -*- coding: utf-8 -*-
import re
from .globals import *
from .utils import *
from flask.ext.redis import Redis

redis = Redis()

def get_room_owner(room_id):
    if room_id != "root":
        roomOwner = redis.get("item:"+item_id+":"+room_id)
        if roomOwner is None:
            return "404 room not found", 404

def search_string(string, fromItem):
    results = []
    words = string.split(" ")
    for i,word in enumerate(words):
        if(len(word)>0):
            searchKey = "item:"+fromItem+":word:"+word+"*"
            wordResults = REDIS_LUA_SEARCH_ITEM(keys=[searchKey])
            if i>0:
                #intersect results if many words
                results = [val for val in results if val in set(wordResults)]
            else:
                results = wordResults
    return results

def get_items(items):
    pipe = redis.pipeline()
    for item in items:
        pipe.hgetall("item:"+item)
    return pipe.execute()

def items_hidden(listKey, numberOfItemsShown):
    itemsLeft = redis.zcard(listKey) - int(numberOfItemsShown)
    if(itemsLeft<0):
        return 0
    return itemsLeft

def make_base_structure():
    # Make root item with id 0
    redis.hset('item:0', 'title', "SortIt!")
    redis.hset('item:0', 'id', "0")
    redis.hset('item:0', 'color', "#FFFFFF")

    # Base children for root item
    global BASE_STRUCTURE_MUSIC_CATEGORY
    global BASE_STRUCTURE_MOVIE_CATEGORY
    global BASE_STRUCTURE_FOUND_BUGS_CATEGORY
    BASE_STRUCTURE_MOVIE_CATEGORY = add_item("Movies", 0)[0]
    BASE_STRUCTURE_MUSIC_CATEGORY = add_item("Musics", 0)[0]
    BASE_STRUCTURE_FOUND_BUGS_CATEGORY = add_item("Bugs and improvements", 0)[0]

    update_ratings([BASE_STRUCTURE_MOVIE_CATEGORY, BASE_STRUCTURE_MUSIC_CATEGORY, BASE_STRUCTURE_FOUND_BUGS_CATEGORY], "0", "root")
    redis_load_user_ratings(BASE_STRUCTURE_MOVIE_CATEGORY)
    redis_load_movie_items()

###
#  Room is always connected to an item. Room contains
#  users personal order for items that he wants to share.
#  Highest item is called Root and it has ID 'root'.
###
def new_room(hostItemID, userID):
    newRoomID = generate_room_id(6)
    while redis.exists("room:"+newRoomID) == 1:
        newRoomID = generate_room_id(6)
    pipe = redis.pipeline()

    pipe.sadd("user:"+userID+":rooms", newRoomID)
    pipe.set("user:"+userID+":"+hostItemID+":room", newRoomID)
    pipe.set("item:"+hostItemID+":"+newRoomID, userID)
    pipe.sadd("item:"+hostItemID+":members", newRoomID)

    if(hostItemID!="root"):
        pipe.zunionstore("room:"+newRoomID+":original", "item:"+hostItemID+":average")
    pipe.execute()
    return newRoomID

###
#   Everything is based on items. Adding an item also adds its title to search index.
#   Search gives results of items inside the item you searched on. searchScopeItem is
#   this parent item.
###
def add_item(title, searchScopeItem, pipe = None):
    searchScopeItem = str(searchScopeItem)
    if pipe is None:
        pipe = redis.pipeline()
        execute = True
    else:
        execute = False

    itemID = str(redis.incr('itemIDCounter'))
    itemColor = random_pastel_color()
    pipe.hset('item:'+itemID, 'id', itemID)
    pipe.hset('item:'+itemID, 'title', title)
    pipe.hset('item:'+itemID, 'color', itemColor)
    pipe.hset('item:'+itemID, 'image', 'placeholder.jpg')
    #add also items which define this items structure
    movieString = re.sub('\([0-9]+\)|[,:!]|[()]', '', title.lower())
    words = movieString.split()
    for word in words:
        pipe.sadd('item:'+searchScopeItem+':word:'+word, itemID+'::'+title)

    if execute is True:
        pipe.execute()
    return [itemID,itemColor]

def add_connection_between_items(itemID, childID, attribute, pipe):
    pipe.hset("item:"+childID+":connected", "attribute", attribute)
    pipe.hset("item:"+childID+":connected", "id", itemID)
    pipe.hset("item:"+itemID, attribute+"_id", childID)

###
#   Updates users ordered list AND average for that parent item
###
def update_ratings(listOfItems, parentItem, user):
    pipe = redis.pipeline()
    counter = 0
    pipe.delete("user:"+user+":"+parentItem)
    for item in reversed(listOfItems):
        counter+=1
        pipe.zadd("user:"+user+":"+parentItem, counter, item)
    pipe.execute()
    # update averages for this parent
    redis_update_item_average(parentItem, user)
    redis_update_connect_item_data(parentItem, user)

def redis_load_movie_items():
    global BASE_STRUCTURE_MOVIE_CATEGORY
    f = open(PROJECT_ROOT+'/ml/umovies.dat', 'r')
    pipe = redis.pipeline()
    for line in f:
        movie = line.decode('utf-8').split("::")
        add_item(movie[1], BASE_STRUCTURE_MOVIE_CATEGORY, pipe)
    pipe.execute()
    f.close()


def redis_load_user_ratings(parentItemID):
    f = open(PROJECT_ROOT+'/ml/uratings.dat', 'r')
    pipe = redis.pipeline()
    for line in f:
        # file format: UserID::MovieID::Rating::Timestamp
        ratings = line.split("::")
        pipe.sadd("file-users", ratings[0])
        # ids in file are not congruent to ids loaded to redis. They have 3 difference.
        movieIDFixed = str(int(ratings[1])+3)
        # load data with small noise so that ratings with same ratings dont have any advantages
        movieRatingNoise = "{:.3f}".format(int(ratings[2])+random.random()*0.2)
        pipe.zadd("file-user:"+ratings[0], movieRatingNoise, movieIDFixed)
        pipe.expire("file-user:"+ratings[0], 60*10)
    pipe.expire("file-users", 60*10)
    pipe.execute()

    users = redis.smembers("file-users")
    for user in users:
        roomID = new_room(BASE_STRUCTURE_MOVIE_CATEGORY, user)
        reviews = redis.zrevrange("file-user:"+user,0,-1)
        update_ratings(reviews, parentItemID, user)

def redis_update_item_average(itemID, userID):
    REDIS_LUA_CALCULATE_AVERAGE_ORDER(keys=[itemID, userID])
def redis_update_connect_item_data(itemID, userID):
    REDIS_LUA_UPDATE_CONNECTED_ITEM(keys=[itemID, userID])

def redis_get_all_view_information(itemID, userID):
    return REDIS_LUA_GET_ITEMS_FROM_ID_LIST(keys=[itemID, userID])

def get_users_ratings(userID, itemID, limit):
    return redis.zrevrange("user:"+userID+":"+str(itemID), 0, limit)

###
# Redis LUA scripts that are loaded into redis on init. SHA strings for these functions are kept on global variables.
###
def load_lua_scripts():
# Fetches all data for lane
    getViewData = """
        local userInfo = redis.call('hmget', 'user:'..KEYS[2]..':'..KEYS[1]..':data', 'id', 'title', 'color', 'image', 'parent', 'title_id', 'color_id', 'image_id', 'parent_id')
        local itemInfo = redis.call('hmget', 'item:'..KEYS[1], "id", "title", "color", "image", "parent", "title_id", "color_id", "image_id", "parent_id")
        for k,v in pairs(userInfo) do
            if v then
                itemInfo[k] = v
            end
        end
        return itemInfo
    """

# This Lua-script provides search functionality
# - It's done with redis command 'keys' with wild card which is bad. Next version should have all words splitted when loading items.
    searchWordLuaScript = """
        local list = redis.call('keys', KEYS[1])
        local result = {}
        local members
        local a = 1
        for i, word in pairs(list) do
            members = redis.call('smembers', word)
            for k,v in pairs(members) do
                result[a] = v
                a = a + 1
            end
        end
        return result
        """
# This LUA script handles updating average lanes. To update average we must firstly remove users votes on that average. That's the reason we have lastAdditionToAverage.
# Much faster to remove last addition and add only this one users sort to average than calculate all sorts inside that item.
    updateAverageWithSteps = """
        local ratings = redis.call('zrevrange', 'user:'..KEYS[2]..':'.. KEYS[1],0,-1)
        local average = redis.call('zrevrange', 'item:'..KEYS[1]..':average',0,-1)
        local ratingsN = table.getn(ratings)
        local averageN = table.getn(average)
        local startingNumber = 100
        redis.call('zunionstore', 'item:'..KEYS[1]..':average', 2, 'item:'..KEYS[1]..':average', 'user:'..KEYS[2]..':'..KEYS[1]..':lastAdditionToAverage', 'WEIGHTS', 1, -1)
        redis.call('del', 'user:'..KEYS[2]..':'..KEYS[1]..':lastAdditionToAverage')
        if startingNumber>0 then
            for i,rating in pairs(ratings) do
                redis.call('zadd', 'user:'..KEYS[2]..':'..KEYS[1]..':lastAdditionToAverage', startingNumber, rating)
                startingNumber = startingNumber - 1
            end
            redis.call('zunionstore', 'item:'..KEYS[1]..':average', 2, 'item:'..KEYS[1]..':average', 'user:'..KEYS[2]..':'..KEYS[1]..':lastAdditionToAverage')
        else
            redis.call('zunionstore', 'item:'..KEYS[1]..':average', 2, 'item:'..KEYS[1]..':average', 'user:'..KEYS[2]..':'..KEYS[1])
        end
    """
# Because you can vote items attributes, for example item TITLE, some items have connections to other items. This script updates possible connected items.
    updateConnectedItem = """
        local connectedItemID = redis.call('hget', 'item:'..KEYS[1]..':connected', 'id')
        local connectedItemAttribute = redis.call('hget', 'item:'..KEYS[1]..':connected', 'attribute')
        if connectedItemID and connectedItemAttribute then
            local firstAverageItemID = redis.call('zrevrange','item:'..KEYS[1]..':average', 0, 0)[1]
            local firstUserItemID = redis.call('zrevrange','user:'..KEYS[2]..':'..KEYS[1], 0, 0)[1]
            local firstAverageItem = redis.call('hget','item:'..firstAverageItemID, connectedItemAttribute)
            local firstUserItem = redis.call('hget','item:'..firstUserItemID, connectedItemAttribute)
            redis.call('hset', 'item:'..connectedItemID, connectedItemAttribute, firstAverageItem)
            redis.call('hset', 'user:'..KEYS[2]..':'..connectedItemID..':data', connectedItemAttribute, firstUserItem)
        end
    """

    global REDIS_LUA_SEARCH_ITEM
    global REDIS_LUA_CALCULATE_AVERAGE_ORDER
    global REDIS_LUA_UPDATE_CONNECTED_ITEM
    global REDIS_LUA_GET_ITEMS_FROM_ID_LIST

    REDIS_LUA_SEARCH_ITEM = redis.register_script(searchWordLuaScript)
    REDIS_LUA_CALCULATE_AVERAGE_ORDER = redis.register_script(updateAverageWithSteps)
    REDIS_LUA_UPDATE_CONNECTED_ITEM = redis.register_script(updateConnectedItem)
    REDIS_LUA_GET_ITEMS_FROM_ID_LIST = redis.register_script(getViewData)

