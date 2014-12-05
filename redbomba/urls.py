from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from redbomba import settings

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^home/$', 'home.views.home'),
                       url(r'^home/logout/$', 'home.views.home_logout'),
                       url(r'^home/login/$', 'home.views.home_login'),
                       url(r'^home/join/$', 'home.views.home_join'),
                       url(r'^home/join/chkEmail/$', 'home.views.home_join_chkEmail'),
                       url(r'^home/join/chkNick/$', 'home.views.home_join_chkNick'),
                       url(r'^home_verify/$', 'home.views.home_verify'),
                       url(r'^$', 'main.views.main'),
                       url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                       )

urlpatterns += staticfiles_urlpatterns()