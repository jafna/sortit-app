# -*- coding: utf-8 -*-

from tests import TestCase
from sortit.redis_functions import redis, add_item, search_string

TEST_SCOPE_ITEM_ID = "test"

class TestRedis(TestCase):

    def test_adding_item(self):
        added_item = add_item('test item number one', TEST_SCOPE_ITEM_ID)
        assert redis.hmget('item:'+added_item[0], 'title') == ['test item number one']
        redis.delete('item:'+added_item[0])

    def test_search(self):
        search_string("test", TEST_SCOPE_ITEM_ID)
