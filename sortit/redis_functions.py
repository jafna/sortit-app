# -*- coding: utf-8 -*-
import re, itertools, time
from flask.ext.redis import Redis
import globals

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
    userItems = get_users_ratings(user, categories, globals.MAX_ITEMS_IN_ONE_SORT)
    userItems.append(item)
    update_ratings(userItems, categories, user)
    return userItems

def fetch_url(url, categories, user, tags):
    itemTitle = redis.get('url:'+url)
    if itemTitle:
        return itemTitle
    else:
        tags.sort()
        redis.set('url_to_user_channel:'+url,
                'user_channel:'+user+':tags:'+'+'.join(tags))
        redis.lpush('redisSpider:start_urls', url)
        return None

def search_string(string):
    results = []
    words = string.split(" ")
    for i,word in enumerate(words):
        if(len(word)>0):
            searchKey = "word:"+word+"*"
            wordResults = globals.REDIS_LUA_SEARCH_ITEM(keys=[searchKey])
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

def update_activities(categories):
    pipe = redis.pipeline()
    #maybe remove possibility to sort in root?
    if len(categories) == 0:
        return
    for i in xrange(1, len(categories)):
        for x in itertools.combinations(categories, i):
            pipe.zadd('tags:'+'+'.join(x)+':activity', time.time(), '+'.join(categories))
    #root contains every activity
    pipe.zadd('tags::activity', time.time(), '+'.join(categories))
    pipe.execute()

###
#   Updates users ordered list AND average
###
def update_ratings(listOfItems, categories, user):
    #limit item count
    listOfItems = listOfItems[:globals.MAX_ITEMS_IN_ONE_SORT+1]
    categories.sort()
    pipe = redis.pipeline()
    counter = 0
    tags = '+'.join(categories)
    pipe.delete('tags:'+tags+":user:"+user)
    for item in reversed(listOfItems):
        counter+=1
        pipe.zadd('tags:'+tags+':user:'+user, counter, item)
    pipe.execute()
    oldAverage = get_average_ratings(categories, globals.MAX_ITEMS_IN_ONE_SORT)
    redis_update_item_average(user, '+'.join(categories))
    newAverage = get_average_ratings(categories, globals.MAX_ITEMS_IN_ONE_SORT)
    #if average has changed, notify possible active clients to update average!
    if(newAverage!=oldAverage):
        redis.publish('tagchannel:'+tags,'averages')
        update_activities(categories)


def redis_update_item_average(userid, tags):
    globals.REDIS_LUA_CALCULATE_AVERAGE_ORDER(keys=["tags:"+tags+":average", "tags:"+tags+":user:"+userid])

def get_activity(categories, limit=-1):
    categories.sort()
    return redis.zrevrange('tags:'+'+'.join(categories)+':activity', 0, limit)

def get_average_ratings(categories, limit=-1):
    categories.sort()
    return redis.zrevrange('tags:'+'+'.join(categories)+':average', 0, limit)

def get_users_ratings(userid, categories, limit=-1):
    categories.sort()
    return redis.zrevrange('tags:'+'+'.join(categories)+':user:'+userid, 0, limit)

def is_adding_item_allowed(item, categories, userid):
    categories.sort()
    pipe = redis.pipeline()
    pipe.zcard('tags:'+'+'.join(categories)+':user:'+userid)
    pipe.zrank('tags:'+'+'.join(categories)+':user:'+userid, item)
    [itemCount, itemRank] = pipe.execute()
    return (itemCount<globals.MAX_ITEMS_IN_ONE_SORT+1) and not itemRank


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
    globals.REDIS_LUA_SEARCH_ITEM = redis.register_script(searchWordLuaScript)
    globals.REDIS_LUA_CALCULATE_AVERAGE_ORDER = redis.register_script(updateAverageWithSteps)

