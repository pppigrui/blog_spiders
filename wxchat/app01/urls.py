from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

import app01
from app01 import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^login/$',views.login),
    url(r'^check_login/$',views.check_login),
    url(r'^index/$',views.index),
    url(r'^avatar/$',views.avatar),
    url(r'^all_contact/$',views.all_contact),
    url(r'^send_msg/$',views.send_msg),
    url(r'^get_msg/$',views.get_msg),
]