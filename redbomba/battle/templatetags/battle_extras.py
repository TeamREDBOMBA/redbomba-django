# -*- coding: utf-8 -*-
from datetime import timedelta

from django import template

register = template.Library()

@register.filter
def date_add(value,arg):
    d = timedelta(days=arg)
    return value+d