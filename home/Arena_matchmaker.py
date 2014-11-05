# -*- coding: utf-8 -*-

 #########################################################################
 # 
 # @contents 메치메이커
 # @file matchmaker.py
 # @auther redbomba.net
 # @maker 이상목
 # @date 2014-02-05
 #
 ################################HISTORY##################################
 #
 # No  WORKER  WORK  DATE  DESCRIPTION
 # 1. 박동혁 PHP->PY변환 2014-02-05 PHP에서 PYTHON으로 변환
 #
 #

from redbomba.home.Func import *
from datetime import timedelta
from redbomba.home.models import LeagueTeam
from redbomba.home.models import LeagueMatch

# Create your views here.

def matchmaker(round):
  sizeholder = []
  indexholder = []
  team_a = []
  team_b = []
  timearray = []
  array = getarray(round)
  start = starttime(round)

  for i in array:
    size = countvalues(i)
    sizeholder.append(size)

  indexholder = sortindex(sizeholder)
  for i in range(len(indexholder)):

    if indexholder[i] != -1:
      time = gettime(array[indexholder[i]])
      for j in range(len(indexholder)):
        if indexholder[j] == -1:
          pass
        elif i==j:
          pass
        elif cmparray(time, array[indexholder[j]]) != -1:
          t = cmparray(time, array[indexholder[j]])
          team_a.append(indexholder[i])
          team_b.append(indexholder[j])
          timearray.append(t)
          indexholder[i] = -1
          indexholder[j] = -1
          break

  #Output goes here
  teamid = team_id(round)
  _team_a = []
  _team_b = []
  ftime = []
  for i in range(len(team_a)):
    _team_a.append(teamid[team_a[i]])
    _team_b.append(teamid[team_b[i]])
    ftime.append(timecal(start,timearray[i]))
  insertteam(_team_a,_team_b,ftime)
  round.is_finish = 1
  round.save()
  retStr = """team_a:%s, team_b:%s, ftime:%s
  <script>
  alert('Success');
  location.href='/arena/';
  </script>""" %(str(_team_a), str(_team_b), str(ftime))
  return retStr

#----------get data from database----------
#Get array of team_id from database
def team_id(round):
  team = []
  query = LeagueTeam.objects.filter(round=round,is_complete=1)
  for i in query:
    if i != None:
      team.append(i)
  return team

#Get array of time from database
def time_array(round):
  feasible_time = []
  query = LeagueTeam.objects.filter(round=round,is_complete=1).values_list('feasible_time', flat=True)
  for i in query:
    if i != None:
      feasible_time.append(i)
  return feasible_time

#Make the array to availiable format
def getarray(round):
  teamtimes = time_array(round)
  thearray = []
  for i in teamtimes:
    teamtimesa = stoa(i)
    thearray.append(teamtimesa)
  return thearray

#Output to database
def insertteam(team_a,team_b,date):
  try:
    for i in range(len(team_a)):
      query = LeagueMatch.objects.create(team_a=team_a[i],team_b=team_b[i],host=0,state=0,result='0',date_match=date[i])
    return True
  except Exception as e:
    return False

#-----------------------------------------------
#---------- functions in main function----------
#-----------------------------------------------
#Convert string to array
def stoa(string):
  array = map(int, string.split(','))
  return array

#Get size of availiable time
def countvalues(array):
  result = 0
  for i in array:
    if i != None:
      result=result+1
  return result

#Find the smallest size in the main array
def getsmallest(array):
  if array != None:
    value1 = getbigvalue(array)
    result = 0
    n = 0
    for i in array:
      if (i < value1) and (i != -1) :
        value1 = i
        result = n
      n=n+1
    return result
  else:
    return False

#Find the beggist value in an array
def getbigvalue(array):
  value1 = 0
  for i in array:
    if i >= value1:
      value1 = i
  return value1+1

#Compare to two arrays if there is anything the same
def cmparray(array1, array2):
  for i in array1:
    result = -1
    if i != -1 and array2.__contains__(i):
      result = i;
      break
  return result

#Sort by size
def sortindex(array):
  indexes = []
  copyarray = array
  for i in copyarray:
    smallest = getsmallest(copyarray)
    indexes.append(smallest)
    copyarray[smallest] = -1
  return indexes

#Get values(times) in an array
def gettime(array):
  recotime = [20,19,18,21,17,14,15,13,12,16,22,23,0,1,2,11,10,9,7,8,3,4,5,6]
  result = []
  for i in recotime:
    for j in range(len(array)):
      if i == array[j]%24:
        result.append(array[j])
  return result

#Time calculator
def starttime(round):
  query = round.start
  return query.replace(hour=0, minute=0, second=0, microsecond=0)

def timecal(datetime,n):
  return datetime + timedelta(hours=n-9)