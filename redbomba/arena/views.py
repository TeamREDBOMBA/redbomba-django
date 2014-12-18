from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from redbomba.arena.models import ArenaBanner


def arena(request):
    if request.user.get_profile().is_pass_gamelink == 0 :
        return HttpResponseRedirect("/head/start/")
    top_banner = ArenaBanner.objects.all().order_by("-id")
    context = {
        'top_banner':top_banner,
        'user': request.user,
        'from':'/arena',
        'appname':'arena'
    }
    return render(request, 'arena.html', context)