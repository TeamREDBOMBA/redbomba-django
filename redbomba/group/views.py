from django.shortcuts import render

# Create your views here.
from redbomba.group.models import Group

def card_group(request):
    groups = request.user.get_profile().get_group()
    context = {
        'user' : request.user,
        'groups':groups,
        'from' : '/stats/',
        'appname':'stats'
    }
    return render(request, 'group.html', context)