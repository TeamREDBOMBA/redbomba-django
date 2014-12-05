from django.shortcuts import render

# Create your views here.

def main(request):
    try:
        context = {
            'user': request.user,
            'from':'/',
            'appname':'main'
            }
    except Exception as e:
        context = {'user': request.user}
    return render(request, 'main.html', context)