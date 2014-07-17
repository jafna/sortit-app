import time,os,hashlib,tldextract,collections
from urlparse import urlparse
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.item import BaseItem
from sortSpider.items import SortItItem
from sortSpider.settings import IMAGES_STORE
from sortSpider.utils import random_pastel_color
import redis

def timestamp():
    ts = time.time()
    return ts

def get_first(iterable, default=None):
    iterable = [x for x in iterable if x]
    if iterable:
        for item in iterable:
            if isinstance(item, collections.Sequence):
                return item[0]
            return item
        return default

def getDomain(url):
    parse_object = urlparse(url)
    domainWithTld = parse_object.netloc
    return tldextract.extract(domainWithTld).domain

def add_item(item):
    if item is None:
        return
    r = redis.Redis()
    channel = r.get('url_to_user_channel:'+item['given_url'])
    title = item['title']
    if r.exists("item:"+title):
        pipe = r.pipeline()
        pipe.set('url:'+item['given_url'],title)
        pipe.set('url:'+item['url'],title)
        pipe.set('url:'+item['response_url'], title)
        pipe.delete('url_to_user_channel:'+item['given_url'])
        pipe.publish(channel, 'item:'+title)
        pipe.execute()
        return
    pipe = r.pipeline()
    itemColor = random_pastel_color()
    #title added to set for easier access
    pipe.hset('item:'+title, 'title', title)
    pipe.hset('item:'+title, 'color', itemColor)
    pipe.hset('item:'+title, 'image', item['images'][0]['path'])
    pipe.hset('item:'+title, 'url', item['url'])

    pipe.set('url:'+item['given_url'],title)
    pipe.set('url:'+item['url'],title)
    pipe.set('url:'+item['response_url'], title)

    #Add item to search index
    words = title.split()
    for word in words:
        pipe.sadd('word:'+word.lower(), 'item:'+title)
    if channel:
        pipe.delete('url_to_user_channel:'+item['given_url'])
        pipe.publish(channel, 'item:'+title)
    pipe.execute()


class RedisspiderSpider(RedisSpider):
    name = 'redisSpider'
    allowed_domains = ['imdb.com', 'ratebeer.com']
    # override method
    def make_requests_from_url(self, url):
        # assign url
        request = Request(url, dont_filter=True)
        request.meta['start_url'] = url
        return request

    def parseItemTitle(self, selector):
        # Selecting interesting title candidates. First in list is most
        # important. ogp.me, schema.org, <meta
        # name="title"> and <head><title>
        titleList = [
                selector.xpath('//meta[@property="og:title"]/@content').extract(),
                selector.xpath('//*[@itemscope=""]//*[@itemprop="name"]').extract(),
                selector.xpath('//meta[@name="title"]/text()').extract(),
                selector.xpath('//head/title[1]/text()').extract()]
        return get_first(titleList)

    def parseItemURL(self, selector, response):
        urlList =[
                selector.xpath('//link[@rel="canonical"]/@href').extract(),
                response.url]
        return get_first(urlList)

    def parseItemImage(self, selector):
        #print selector.xpath('//img[contains(@src,"base64")/@src]').extract()
        imgList = [
                selector.xpath('//meta[@property="og:image"]/@content').extract(),
                selector.xpath('//*[@itemscope=""]//*[@itemprop="image"]/@src').extract(),
                selector.xpath('//img/@src').extract()]
        urlToImg = get_first(imgList)
        return urlToImg

    def handleDomainSpecificTricks(self, url, selector):
        domain = getDomain(url)
        alternateUrl = selector.xpath('//link[@rel="alternate"]/@href').extract()
        # when on amazon, visit alternate link for cleaner data
        if domain=='amazondisabled' and alternateUrl:
            return Request(alternateUrl)
        return None
    # Spider main method
    def parse(self, response):
        selector = Selector(response)
        request = self.handleDomainSpecificTricks(response.url, selector)
        if request:
            return request
        item = SortItItem()
        item['title'] = self.parseItemTitle(selector)
        item['image_urls'] = [self.parseItemImage(selector)]
        item['url'] = self.parseItemURL(selector, response)
        item['response_url'] = response.url
        item['given_url'] = response.meta['start_url']
        if not item['title'] or len(filter(None,item['image_urls']))==0:
            r = redis.Redis()
            channel = r.get('url_to_user_channel:'+item['given_url'])
            r.publish(channel, 'error')
            r.delete('url_to_user_channel:'+item['given_url'])
            return None
        return item

