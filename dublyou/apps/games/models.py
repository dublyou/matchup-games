from django.db import models
from django.contrib.auth.models import User
from ...constants import GAMES_CLASSES, COMP_TYPES, STATES, RULE_TYPES
# from django.core.validators import RegexValidator, EmailValidator
# from django.utils.translation import ugettext_lazy as _


class GameType(models.Model):
    game_name = models.CharField(max_length=30, unique=True)
    game_class = models.IntegerField(choices=GAMES_CLASSES)
    game_subclass = models.CharField(max_length=25)
    game_rules = models.TextField(max_length=500)
    comp_type = models.IntegerField(choices=COMP_TYPES)
    comp_per_team = models.IntegerField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_game_class_display() + "|" + self.game_subclass + "|" + self.game_name


class GameRule(models.Model):
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE)
    rule = models.CharField(max_length=50)
    rule_type = models.IntegerField(choices=RULE_TYPES)


class GameVenue(models.Model):
    venue_name = models.CharField(max_length=30, unique=True)
    street_address = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    state = models.CharField(choices=STATES, max_length=2)
    zip_code = models.CharField(max_length=5)
    game_type = models.ManyToManyField(GameType)
    venue_type = models.IntegerField(choices=((1, "private"), (2, "public")))
