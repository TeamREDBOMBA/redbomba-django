from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from home.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

base64_pattern = r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'redbomba.views.home', name='home'),
    # url(r'^redbomba/', include('redbomba.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^$', main),
    (r'^home/$', home),
    (r'^stats/$', stats),
    (r'^stats/(?P<username>.*)$', stats),
    (r'^arena/$', arena),
    (r'^battle/$', battle),
    (r'^s/$', summoner),
    (r'^feed/private/$', read_Feed_pri),
    (r'^feed/public/$', read_Feed_pub),
    (r'^feed/card/$', read_Feed_card),
    (r'^reply/$', read_Reply),
    (r'^group/$', getGroup),
    (r'^groupinfo/$', getGroupInfo),
    (r'^groupinfoorder/$', getGroupInfoOrder),
    (r'^card/$', getCard),
    (r'^matchmaker/$', setMatchmaker),
    (r'^group/fnc/name/$', fncGroupName),
    (r'^group/fnc/nick/$', fncGroupNick),
    (r'^groupmember/$', getGroupMember),
    (r'^grouplist/$', getGroupList),
    (r'^searchlist/$', getSearchBar),
    (r'^field/$', getField),
    (r'^noti/$', read_Notification),
    (r'^forsocket/$', forsocket),
    (r'^chatting/$', getChatting),
    (r'^myarena/$', getMyarena),
    (r'^cardbtn/$', getLargeCardBtn),
    (r'^db/smile/$', setSmile),
    (r'^db/noti/$', write_Notification),
    (r'^db/feed/$', write_Feed),
    (r'^db/reply/$', write_Reply),
    (r'^db/gamelink/$', write_GameLink),
    (r'^db/group/$', write_Group),
    (r'^db/groupmember/$', setGroupMember),
    (r'^db/grouplist/$', setGroupList),
    (r'^db/leagueteam/$', setLeagueteam),
    (r'^db/tutorial/$', setTutorial),
    (r'^auth/login/$', email_login_view),
    (r'^auth/logout/$', logout_page),
    (r'^auth/signup/$', register_page),
    (r'^auth/fnc/email/$', fncSignupEmail),
    (r'^auth/fnc/nick/$', fncSignupNick),
    (r'^auth/(?P<id>\d+)/(?P<date_joined>{})'.format(base64_pattern), verifyEmail),
    (r'^mobile/$', fromMobile),
    (r'^test/$', test),
)
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))