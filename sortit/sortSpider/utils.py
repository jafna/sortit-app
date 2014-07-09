# -*- coding: utf-8 -*-
import random

def random_pastel_color():
    r = lambda: random.randint(0,255)
    color = r(), r(), r()
    return lighten_color_and_return_hex(color)

def lighten_color_and_return_hex(rgb):
    return '#%02X%02X%02X' % ((rgb[0]+255)/2,(rgb[1]+255)/2,(rgb[2]+255)/2)

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))
