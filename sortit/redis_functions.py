# -*- coding: utf-8 -*-
import re
from .globals import *
from .utils import *
from flask.ext.redis import Redis

redis = Redis()

def event_stream(channels):
    pubsub = redis.pubsub()
    for i in channels:
        pubsub.subscribe(i)
    try:
        for message in pubsub.listen():
            yield 'data: %s\n\n' % message['data']
    except:
        for i in channels:
            pubsub.unsubscribe(i)

def add_item_for_user(item, categories, user):
    userItems = get_users_ratings(user, categories)
    userItems.append(item)
    update_ratings(userItems, categories, user)
    return userItems

def fetch_url(url, categories, user):
    if redis.exists('url:'+url):
        return False
    else:
        redis.lpush('redisSpider:start_urls', url)
        redis.set('url_user:'+url, user)
        return True

def search_string(string):
    results = []
    words = string.split(" ")
    for i,word in enumerate(words):
        if(len(word)>0):
            searchKey = "word:"+word+"*"
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
        pipe.hgetall(item)
    return pipe.execute()

###
#   Updates users ordered list AND average
###
def update_ratings(listOfItems, categories, user):
    categories.sort()
    pipe = redis.pipeline()
    counter = 0
    tags = '+'.join(categories)
    pipe.delete(tags+":user:"+user)
    for item in reversed(listOfItems):
        counter+=1
        pipe.zadd('tags:'+tags+':user:'+user, counter, item)
    pipe.execute()
    oldAverage = get_average_ratings(categories)
    redis_update_item_average(user, '+'.join(categories))
    newAverage = get_average_ratings(categories)
    #if average has changed, notify possible active clients to update average!
    if(newAverage!=oldAverage):
        redis.publish('tagchannel:'+tags,'averages')

def redis_update_item_average(userid, tags):
    REDIS_LUA_CALCULATE_AVERAGE_ORDER(keys=["tags:"+tags+":average", "tags:"+tags+":user:"+userid])

def get_average_ratings(categories, limit=-1):
    categories.sort()
    return redis.zrevrange('tags:'+'+'.join(categories)+':average', 0, limit)

def get_users_ratings(userid, categories, limit=-1):
    categories.sort()
    return redis.zrevrange('tags:'+'+'.join(categories)+':user:'+userid, 0, limit)

###
# Redis LUA scripts that are loaded into redis on init. SHA strings for these functions are kept on global variables.
###
def load_lua_scripts():
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

    updateAverageWithSteps = """
        local ratings = redis.call('zrevrange', KEYS[2],0,-1)
        local average = redis.call('zrevrange', KEYS[1],0,-1)
        local ratingsN = table.getn(ratings)
        local averageN = table.getn(average)
        local startingNumber = 100
        redis.call('zunionstore', KEYS[1], 2, KEYS[1], KEYS[2]..':lastAdditionToAverage', 'WEIGHTS', 1, -1)
        redis.call('del', KEYS[2]..':lastAdditionToAverage')
        if startingNumber>0 then
            for i,rating in pairs(ratings) do
                redis.call('zadd', KEYS[2]..':lastAdditionToAverage', startingNumber, rating)
                startingNumber = startingNumber - 1
            end
            redis.call('zunionstore', KEYS[1], 2, KEYS[1], KEYS[2]..':lastAdditionToAverage')
        else
            redis.call('zunionstore', KEYS[1], 2, KEYS[1], KEYS[2])
        end
    """
    global REDIS_LUA_SEARCH_ITEM
    global REDIS_LUA_CALCULATE_AVERAGE_ORDER

    REDIS_LUA_SEARCH_ITEM = redis.register_script(searchWordLuaScript)
    REDIS_LUA_CALCULATE_AVERAGE_ORDER = redis.register_script(updateAverageWithSteps)

