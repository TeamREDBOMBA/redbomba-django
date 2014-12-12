from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from redbomba.main.models import GlobalCard


def main(request):
    try:
        if request.user.get_profile().is_pass_gamelink == 0 :
            return HttpResponseRedirect("/head/start/")
        context = {
            'user': request.user,
            'from':'/',
            'appname':'main'
            }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'main.html', context)