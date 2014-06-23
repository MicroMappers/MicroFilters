from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.index', name='index'),
    url(r'^download/$', 'core.views.downloadPage', name='download'),
    url(r'^getAppList/$', 'core.views.getAppList', name='applist'),
    url(r'^admin/', include(admin.site.urls)),
)
