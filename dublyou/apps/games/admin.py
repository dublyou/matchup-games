from django.contrib import admin
from .models import Game, GameVenue, GameRule

admin.site.register(Game)
admin.site.register(GameRule)
admin.site.register(GameVenue)
