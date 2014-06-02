# -*- coding: utf-8 -*-

from sortit.utils import generate_room_id,hex_to_rgb,lighten_color_and_return_hex
from tests import TestCase

ILLEGAL_CHARS = set('!"#¤%&/()=?*')
class TestUtils(TestCase):
    def test_room_id_generation(self):
        room_id = generate_room_id(10)
        assert len(room_id) == 10
        assert not any((c in ILLEGAL_CHARS) for c in room_id)

    def test_hex_to_rgb(self):
        # googled some hex values and their rgb counter parts
        hex_rgb_pairs = {
		'#000000':(0,0,0),#black
		'#FF0000':(255,0,0),#red
		'#00FF00':(0,255,0),#green
		'#0000FF':(0,0,255),#blue
		'#C0C0C0':(192,192,192),#gray
		'#FF00FF':(255,0,255),#magenta
		'#FFFFFF':(255,255,255)}#white
        for key, value in hex_rgb_pairs.iteritems():
            assert hex_to_rgb(key) == value

    def test_color_lightment(self):
        colors = [(255,0,0),(0,255,0)]
        for color in colors:
            lighten_hex = lighten_color_and_return_hex(color)
            lighten = hex_to_rgb(lighten_hex)
            # rgb has a cap of 255
            assert color[0]<lighten[0] or (color[0]==255 and lighten[0]==255)
            assert color[1]<lighten[1] or (color[1]==255 and lighten[1]==255)
            assert color[2]<lighten[2] or (color[2]==255 and lighten[2]==255)
