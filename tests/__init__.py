# -*- coding: utf-8 -*-
"""
    Unit Tests
    ~~~~~~~~~~
"""

from flask.ext.testing import TestCase as Base

from sortit import create_app
from sortit.redis_functions import redis, make_base_structure

TEST_SCOPE_ITEM_ID = "test"

class TestCase(Base):
    def create_app(self):
        """Create and return a testing flask app."""
        app = create_app()
        return app

    def init_data(self):
        """init possible data"""

    def setUp(self):
        """Reset all tables before testing."""

    def tearDown(self):
        """Clean db session and drop all tables."""

    def _test_get_request(self, endpoint, template=None):
        response = self.client.get(endpoint)
        self.assert_200(response)
        if template:
            self.assertTemplateUsed(name=template)
        return response
