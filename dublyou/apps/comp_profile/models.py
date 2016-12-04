from django.db import models
from django.conf import settings
# from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    # Relations
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        verbose_name=_("user")
    )

    abbrev = models.CharField(max_length=6)
    mobile_number = models.IntegerField(unique=True)
    zip_code = models.IntegerField()
    creation_datetime = models.DateTimeField(auto_now_add=True)

    # Custom Properties
    @property
    def username(self):
        return self.user.username

    # Methods

    # Meta and String
    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user",)

    def __str__(self):
        return self.user.username
