from cStringIO import StringIO
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from redisSpider import add_item

import os

from PIL import Image

class CustomImagesPipeline(ImagesPipeline):

	def get_images(self, response, request, info):
		path = self.file_path(request, response=response, info=info)
		orig_image = Image.open(StringIO(response.body))
		size = (122,230)
		image, buf = self.convert_image(orig_image, size)
		yield path, image, buf

        def item_completed(self, results, item, info):
                if self.IMAGES_RESULT_FIELD in item.fields:
                        item[self.IMAGES_RESULT_FIELD] = [x for ok, x in results if ok]
                        add_item(item)
                return item
