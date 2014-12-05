from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from redbomba import settings

admin.autodiscover()

base64_pattern = r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'

urlpatterns = patterns('',
                       url(r'^$', 'redbomba.main.views.main'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^home/$', 'redbomba.home.views.home'),
                       url(r'^home/logout/$', 'redbomba.home.views.home_logout'),
                       url(r'^home/login/$', 'redbomba.home.views.home_login'),
                       url(r'^home/join/$', 'redbomba.home.views.home_join'),
                       url(r'^home/join/chkEmail/$', 'redbomba.home.views.home_join_chkEmail'),
                       url(r'^home/join/chkNick/$', 'redbomba.home.views.home_join_chkNick'),
                       url(r'^home/verify/(?P<id>\d+)/(?P<date_joined>{})'.format(base64_pattern), 'redbomba.home.views.home_verify'),
                       url(r'^main/globalcard/$', 'redbomba.main.views.main_globalcard'),
                       url(r'^head/userinfo/$', 'redbomba.head.views.head_userinfo'),

                       url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                       )

urlpatterns += staticfiles_urlpatterns()