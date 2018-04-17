from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from ...constants import GAMES_CLASSES, MATCHUP_TYPES, STATES, RULE_TYPES
from ...utils import upload_to_path
# from django.core.validators import RegexValidator, EmailValidator
# from django.utils.translation import ugettext_lazy as _


class Game(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=500)
    game_type = models.IntegerField(choices=GAMES_CLASSES)
    matchup_type = models.IntegerField(choices=MATCHUP_TYPES, null=True, blank=True)
    players_per_team = models.IntegerField(null=True, blank=True)
    inventor = models.CharField(max_length=50, null=True, blank=True)
    creator = models.ForeignKey(User)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    default_game = models.BooleanField(default=False)
    game_image = models.ImageField(upload_to=upload_to_path, null=True, blank=True)

    @property
    def profile_image(self):
        if self.game_image:
            return self.game_image.url
        return "/static/svg/profile_game.png"

    def __str__(self):
        return self.name

    # Methods
    def get_absolute_url(self):
        return reverse('game', kwargs={"pk": self.id})

    # Meta and String
    class Meta:
        ordering = ("name",)


class GameRule(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_rules")
    rule = models.CharField(max_length=100)
    rule_type = models.IntegerField(choices=RULE_TYPES)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class GameStat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_stats")
    name = models.CharField(max_length=50, unique=True)
    abbrev = models.CharField(max_length=4, null=True, blank=True)
    formula = models.CharField(max_length=30, null=True, blank=True)
    value_type = models.IntegerField(choices=((1, "number"), (2, "percentage")), default=1)
    decimal_places = models.IntegerField(default=0)
    min_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    # Meta and String
    class Meta:
        unique_together = (("game", "name"), ("game", "abbrev"))
        ordering = ("name",)


class GameVenue(models.Model):
    name = models.CharField(max_length=50, unique=True)
    street_address = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    state = models.CharField(choices=STATES, max_length=2)
    zip_code = models.CharField(max_length=5)
    games = models.ManyToManyField(Game)
    venue_type = models.IntegerField(choices=((1, "private"), (2, "public")))
