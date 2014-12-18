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
   url(r'^head/start/$', 'redbomba.head.views.head_start'),
   url(r'^head/userinfo/$', 'redbomba.head.views.head_userinfo'),
   url(r'^head/gamelink/$', 'redbomba.head.views.head_gamelink'),
   url(r'^head/gamelink/list/$', 'redbomba.head.views.head_gamelink_list'),
   url(r'^head/gamelink/login/$', 'redbomba.head.views.head_gamelink_login'),
   url(r'^head/gamelink/link/$', 'redbomba.head.views.head_gamelink_link'),
   url(r'^head/gamelink/load/$', 'redbomba.head.views.head_gamelink_load'),
   url(r'^head/gamelink/delete/$', 'redbomba.head.views.head_gamelink_delete'),
   url(r'^head/gamelink/skip/$', 'redbomba.head.views.head_gamelink_skip'),
   url(r'^arena/$', 'redbomba.arena.views.arena'),
   url(r'^card/global/$', 'redbomba.main.views.card_global'),
   url(r'^card/global/large/(?P<fid>\d+)$', 'redbomba.main.views.card_global_large'),
   url(r'^feed/$', 'redbomba.feed.views.feed'),
   url(r'^feed/post/$', 'redbomba.feed.views.feed_post'),
   url(r'^feed/reply/$', 'redbomba.feed.views.feed_reply'),
   url(r'^feed/reply/post/$', 'redbomba.feed.views.feed_reply_post'),
   url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
   )

urlpatterns += staticfiles_urlpatterns()