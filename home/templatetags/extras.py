# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from django.utils.timezone import utc
from django.utils import timezone
from django import template
from redbomba.home.models import GameLink

register = template.Library()

@register.filter
def date_add(value,arg):
  d = timedelta(days=arg)
  return value+d

@register.filter
def get_gamelink(value):
  try:
    return GameLink.objects.get(uid=value).name
  except Exception as e:
    return "연결된 게임이 없습니다."

@register.filter
def get_time_diff(date_data,arg):
	now = datetime.utcnow().replace(tzinfo=utc)
	diffMsg = {}
	if now > date_data :
		if arg == "state":
			return 0
		timediff = now - date_data
		timediff = timediff.total_seconds()
		if timediff > 259200:
			return date_data.strftime('%m월 %d일')
		elif timediff > 86400:
			return str(int(timediff/3600/24))+"일 전"
		elif timediff > 3600:
			return str(int(timediff/3600))+"시간 전"
		elif timediff > 60:
			return str(int(timediff/60))+"분 전"
		else :
			return 0
	else :
		now = datetime.utcnow().replace(tzinfo=utc)
		timediff = date_data - now
		timediff = timediff.total_seconds()
		if arg == "state":
			return 1
		if timediff < 0 :
			return 0
		elif timediff < 60:
			return str(int(timediff))+"초 후"
		elif timediff < 3600:
			return str(int(timediff/60))+"분 후"
		elif timediff < 86400:
			return str(int(timediff/3600))+"시간 후"
		else :
			return str(int(timediff/86400))+"일 후"

@register.filter
def sub( value, arg ):
    try:
        value = int( value )
        arg = int( arg )
        if arg: return value - arg
    except: pass
    return ''

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