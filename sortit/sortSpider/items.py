from scrapy.item import Item, Field

class SortItItem(Item):
    title = Field()
    image_urls = Field()
    images = Field()
    url = Field()
