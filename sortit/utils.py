# -*- coding: utf-8 -*-

import random, string

def generate_room_id(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))




