from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.games_view),
    url(r'^new/$', views.new_game),
]
