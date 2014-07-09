import time
import os
import hashlib
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from sortSpider.items import SortItItem
from sortSpider.settings import IMAGES_STORE
from sortSpider.utils import random_pastel_color
import redis

def timestamp():
    ts = time.time()
    return ts

def add_item(item):
    if item is None:
        return
    r = redis.Redis()
    userId = r.get('url_user:'+item['url'])
    pipe = r.pipeline()
    itemColor = random_pastel_color()
    title = item['title'][0]
    #title added to set for easier access
    pipe.hset('item:'+title, 'title', title)
    pipe.hset('item:'+title, 'color', itemColor)
    pipe.hset('item:'+title, 'image', item['images'][0]['path'])
    pipe.hset('item:'+title, 'url', item['url'])
    #Add item to search index
    words = title.split()
    for word in words:
        pipe.sadd('word:'+word.lower(), 'item:'+title)
    pipe.publish('userchannel:'+userId, 'item:'+title)
    pipe.execute()


class RedisspiderSpider(RedisSpider):
    name = 'redisSpider'
    allowed_domains = ['imdb.com', 'media-imdb.com']
    def isOpenGraph(self, response):
        sel = Selector(response)
        htmlAttributes =  sel.xpath('//html/@*').extract()
        if any("ogp.me" in s or "opengraphprotocol.org" in s for s in htmlAttributes):
            return True
        return False

    def isSchemaOrg(self, response):
        sel = Selector(response)
        if sel.xpath('//@itemscope').extract() is not '':
            return True
        return False


    def parseOpenGraph(self, response):
        selector = Selector(response)
        item = SortItItem()
        item['title'] = selector.xpath('//meta[@property="og:title"]/@content').extract()
        item['url'] = response.url
        item['image_urls'] = selector.xpath('//meta[@property="og:image"]/@content').extract()
        return item

    def parseSchemaOrg(self, selector):
        return None

    def parse(self, response):
        item = None
        if self.isOpenGraph(response):
            item = self.parseOpenGraph(response)
        elif self.isSchemaOrg(response):
            item = self.parseSchemaOrg(response)
        return item

