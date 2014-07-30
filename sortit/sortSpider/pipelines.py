from cStringIO import StringIO
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from redisSpider import addItem
from scrapy.utils.misc import md5sum

import os

from PIL import Image
global biggestItem
biggestItem = {'width':0, 'height':0}

class CustomImagesPipeline(ImagesPipeline):
    def image_downloaded(self, response, request, info):
        global biggestItem
        checksum = None
        for path, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            width, height = image.size
            if biggestItem['width']*biggestItem['height']<width*height:
                biggestItem = {'width':width, 'height':height, 'path':path, 'buf':buf,'info':info}
        return checksum

    def get_images(self, response, request, info):
        path = self.file_path(request, response=response, info=info)
        orig_image = Image.open(StringIO(response.body))
        size = (122,290)
        image, buf = self.convert_image(orig_image, size)
        yield path, image, buf

    def item_completed(self, results, item, info):
        global biggestItem
        self.store.persist_file(
                biggestItem['path'], biggestItem['buf'], biggestItem['info'],
                meta={'width': biggestItem['width'], 'height': biggestItem['height']},
                headers={'Content-Type': 'image/jpeg'})
        if self.IMAGES_RESULT_FIELD in item.fields:
            item[self.IMAGES_RESULT_FIELD] = biggestItem['path']
            addItem(item)
        biggestItem = {'width':0,'height':0}
        return item
