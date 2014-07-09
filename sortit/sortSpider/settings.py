# Scrapy settings for sortSpider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'sortSpider'

SPIDER_MODULES = ['sortSpider.spiders']
NEWSPIDER_MODULE = 'sortSpider.spiders'


DEFAULT_ITEM_CLASS = 'sortSpider.items.SortItItem'
ITEM_PIPELINES = {'sortSpider.pipelines.CustomImagesPipeline': 1}
IMAGES_STORE = '/home/mika/sortit-master/sortit/static/item_images/'

DEFAULT_REQUEST_HEADERS = {
            'Accept-Language': 'en'
        }
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'sortSpider (+http://www.yourdomain.com)'


