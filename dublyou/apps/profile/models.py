from django.db import models
from django.conf import settings
# from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

from django.urls import reverse
import datetime as dt
import geocoder as geo


class Profile(models.Model):
    def upload_to_path(self, filename):
        print(filename)
        file_ext = filename.split(".")[-1]
        path = "media/img/{}/{}.{}".format(self.__class__.__name__.lower(),
                                           self.id,
                                           file_ext)
        return path
    # Relations
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        verbose_name=_("user")
    )
    friends = models.ManyToManyField("self", related_name="friends", blank=True)
    profile_type = models.IntegerField(choices=((1, "player"),), default=1)
    privacy_type = models.IntegerField(choices=((1, "private"), (2, "public")), default=1)
    bio = models.CharField(max_length=200, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    gender = models.IntegerField(choices=((0, "male"), (1, "female")), null=True)
    abbrev = models.CharField(max_length=6, unique=True, null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\([0-9]{3}\) [0-9]{3}-[0-9]{4}$',
                                 message="Phone number must be entered in the format: '(xxx) xxx-xxxx'. Up to 10 digits allowed.")
    mobile_number = models.CharField(max_length=14, unique=True, validators=[phone_regex], null=True, blank=True)
    current_zip = models.CharField(max_length=5, null=True, blank=True)
    current_city = models.CharField(max_length=30, null=True, blank=True)
    current_state = models.CharField(max_length=3, null=True, blank=True)
    hometown_zip = models.CharField(max_length=5, null=True, blank=True)
    hometown_city = models.CharField(max_length=30, null=True, blank=True)
    hometown_state = models.CharField(max_length=3, null=True, blank=True)
    user_image = models.ImageField(upload_to=upload_to_path, null=True, blank=True)
    bg_image = models.FileField(upload_to="dublyou/static/img/profile/bg", null=True, blank=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    # Custom Properties
    @property
    def username(self):
        return self.user.username

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def age(self):
        if self.birth_date:
            return int((dt.date.today() - self.birth_date).days / 365)

    @property
    def height_string(self):
        if self.height:
            return "{}-{}".format(int(self.height/12), self.height % 12)

    @property
    def profile_image(self):
        if self.user_image:
            return self.user_image.url
        else:
            return "/static/svg/profile_inv.png"

    @property
    def current_location(self):
        if self.current_zip:
            return "{}, {}".format(self.current_city, self.current_state)

    @property
    def hometown_location(self):
        if self.hometown_zip:
            return "{}, {}".format(self.hometown_city, self.hometown_state)

    @property
    def teams(self):
        return self.team_set.all()

    @property
    def leagues(self):
        return self.comm_leagues.all()

    @property
    def competitions(self):
        return self.competitors.select_related('competition').only('competition')

    @property
    def invite_count(self):
        return self.competition_invites.count() + self.league_invites.count()

    # Methods
    def get_absolute_url(self):
        return reverse('profile', kwargs={"pk": self.id})

    # Meta and String
    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user",)

    def __str__(self):
        return self.user.get_full_name() + (" ({})".format(self.abbrev) if self.abbrev else "")

    def save(self, *args, **kwargs):
        if self.pk:
            orig = Profile.objects.get(pk=self.pk)
            zip_types = []
            if orig.current_zip != self.current_zip:
                zip_types.append("current")
            if orig.hometown_zip != self.hometown_zip:
                zip_types.append("hometown")
            self.set_city_state_from_zip(zip_types=zip_types)
        else:
            self.set_city_state_from_zip()

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
        Profile.objects.create(user=instance)


class FriendRequests(models.Model):
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend_requests_sent")
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend_requests")
    status = models.IntegerField(choices=((0, "denied"), (1, "pending"), (2, "approved")))
