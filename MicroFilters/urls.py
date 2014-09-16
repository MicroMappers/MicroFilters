from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.index', name='index'),
    url(r'^download/', 'core.views.downloadPage', name='download'),
    url(r'^listFiles/(?P<userNo>[\w\d-]{0,50})', 'core.views.getFileList'),
    url(r'^uploadProgress/(?P<uuid>[\w\d]{0,50})/$', 'core.views.uploadProgress', name='upload-progress'),
    url(r'^getAppList/$', 'core.views.getAppList', name='applist'),
    url(r'^admin/', include(admin.site.urls)),
)
