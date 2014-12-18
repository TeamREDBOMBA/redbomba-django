# -*- coding: utf-8 -*-
from datetime import timedelta

from django import template
from redbomba.home.models import get_time_difference

register = template.Library()

@register.filter
def get_time_diff(date_data,arg):
    return get_time_difference(date_data,arg)

@register.filter
def date_add(value,arg):
    d = timedelta(days=arg)
    return value+d

@register.filter
def get_gamelinks(group,game):
    return group.get_gamelinks(game=game)

@register.filter
def getLine( value, arg ):
    value = value.split('\n')
    return value[arg]

@register.filter
def getRange( value ):
    return range(int(value))

@register.filter
def getMatch(league, round):
    return league.get_league_match(round)

@register.filter
def sub_time(date_data,arg):
    arg = int(arg)
    return date_data-timedelta(minutes=arg)

@register.filter
def sub( value, arg ):
    try:
        value = int( value )
        arg = int( arg )
        if arg: return value - arg
    except: pass
    return ''