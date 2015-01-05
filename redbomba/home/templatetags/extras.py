# -*- coding: utf-8 -*-

from django import template
from redbomba.home.models import get_time_difference

register = template.Library()

@register.filter
def get_time_diff(date_data,arg):
    return get_time_difference(date_data,arg)