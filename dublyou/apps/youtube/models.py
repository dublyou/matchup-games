from django.db import models
from django.dispatch import Signal
from django.utils.translation import ugettext as _

from ..competitions.models import Matchup
from ..profile.models import Profile


class MatchupVideo(models.Model):
    matchup = models.ForeignKey(Matchup, related_name="videos")
    uploaded_by = models.ForeignKey(Profile, related_name="videos")
    video_id = models.CharField(max_length=255, unique=True, primary_key=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class UploadedVideo(models.Model):
    """
    temporary video object that is uploaded to use in direct upload
    """

    file_on_server = models.FileField(upload_to='videos', null=True,
                                      help_text=_("Temporary file on server for \
                                              using in `direct upload` from \
                                              your server to youtube"))

    def __unicode__(self):
        """string representation"""
        return self.file_on_server.url
#
# Signal Definitions
#

video_created = Signal(providing_args=["video"])
