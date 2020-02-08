from django.urls import path
from prj.views import login, top, callback
urlpatterns = [
    path('login', login),
    path('callback', callback),
    path('', top),
]
