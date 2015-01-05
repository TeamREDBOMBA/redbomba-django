# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter
def sub( value, arg ):
    try:
        value = int( value )
        arg = int( arg )
        if arg: return value - arg
    except: pass
    return ''