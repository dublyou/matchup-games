from django.db import models
from django.conf import settings
# from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from ..games.models import GameType
from django.template.loader import render_to_string
from django.urls import reverse
import datetime as dt
import geocoder as geo


class Profile(models.Model):
    # Relations
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        verbose_name=_("user")
    )
    activation_key = models.CharField(max_length=40, null=True)
    privacy_type = models.IntegerField(choices=((1, "private"), (2, "public")), default=1)
    key_expires = models.DateTimeField(null=True)
    bio = models.CharField(max_length=200, null=True)
    birth_date = models.DateField(null=True)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    gender = models.IntegerField(choices=((0, "male"), (1, "female")), null=True)
    abbrev = models.CharField(max_length=6, unique=True)
    phone_regex = RegexValidator(regex=r'^\d{10}$',
                                 message="Phone number must be entered in the format: '999999999'. Up to 10 digits allowed.")
    mobile_number = models.CharField(max_length=10, unique=True, validators=[phone_regex])
    current_zip = models.CharField(max_length=5, null=True)
    current_city = models.CharField(max_length=30, null=True)
    current_state = models.CharField(max_length=3, null=True)
    hometown_zip = models.CharField(max_length=5, null=True)
    hometown_city = models.CharField(max_length=30, null=True)
    hometown_state = models.CharField(max_length=3, null=True)
    user_image = models.ImageField(upload_to="media/img/profile/user", null=True)
    bg_image = models.FileField(upload_to="dublyou/static/img/profile/bg", null=True)
    rating = models.DecimalField(default=0, decimal_places=4, max_digits=5)
    favorite_game = models.ManyToManyField(GameType)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    # Custom Properties
    @property
    def username(self):
        return self.user.username

    @property
    def age(self):
        return int((dt.date.today() - self.birth_date).days / 365)

    @property
    def current_city_state(self):
        return "{}, {}".format(self.current_city, self.current_state)

    @property
    def hometown_city_state(self):
        return "{}, {}".format(self.hometown_city, self.hometown_state)

    @property
    def team_list(self):
        return render_to_string("dropdown_list.html", self.user.team_set.all())

    @property
    def league_list(self):
        return render_to_string("dropdown_list.html", self.user.leagues.all())

    @property
    def wins(self):
        return self.user.matchup_member_set.filter(place=1, matchup__status=3).count()

    @property
    def games_played(self):
        return self.user.matchup_member_set.filter(matchup__status=3).count()

    @property
    def win_perc(self):
        return round(self.wins / self.games_played, 3) * 100

    @property
    def record(self):
        return self.record_string(self.wins, self.games_played)

    @property
    def team_wins(self):
        return self.matchup_members.filter(place=1, matchup__status=3).count()

    @property
    def team_games_played(self):
        return self.matchup_members.filter(matchup__status=3).count()

    @property
    def team_record(self):
        return self.record_string(self.team_wins, self.team_games_played)

    @property
    def matchup_members(self):
        return self.user.team_set.prefetch_related('matchup_member_set').all()

    @property
    def competitions(self):
        return self.user.leagues.prefetch_related('competitions').all()

    @property
    def competitions_page(self):
        return render_to_string("competitions.html", self.competitions)

    @property
    def schedule(self):
        return self.user.matchups.filter(status__in=[1, 2, 5, 6]).all()

    @property
    def schedule_page(self):
        return render_to_string("matchups.html", self.upcoming_matchups)

    @property
    def results(self):
        return self.user.matchups.filter(status=3).all()

    @property
    def results_page(self):
        return render_to_string("matchup_results.html", self.matchup_results)

    # Methods
    def get_absolute_url(self):
        return reverse('profile:detail', args=[str(self.id)])

    def permissions(self, user):
        if user == self.user:
            return "edit"
        elif self.privacy_type == 2:
            return "view"
        else:
            return "none"

    def record_string(self, wins, games_played):
        if games_played > 0:
            return "{}-{} ({} %)".format(wins, games_played - wins, round(wins / games_played, 3) * 100)

    # Meta and String
    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user",)

    def __str__(self):
        return self.user.get_full_name() + (" ({})".format(self.abbrev) if self.abbrev else "")

    def save(self, *args, **kwargs):
        if self.pk:
            self.set_city_state_from_zip()
        else:
            orig = Profile.objects.get(pk=self.pk)
            zip_types = []
            if orig.current_zip != self.current_zip:
                zip_types.append("current")
            if orig.hometown_zip != self.hometown_zip:
                zip_types.append("hometown")
            self.set_city_state_from_zip(zip_types=zip_types)

        super(Profile, self).save(*args, **kwargs)

    def set_city_state_from_zip(self, zip_types=None):
        zip_types = zip_types or ["current", "hometown"]

        for name in zip_types:
            zip_code = getattr(self, name + "_zip")
            if zip_code:
                location = geo.google(zip_code)
                setattr(self, name + "_city", location.city)
                setattr(self, name + "_state", location.state)


from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()