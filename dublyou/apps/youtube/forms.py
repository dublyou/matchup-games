from django import forms

from .youtube_upload.main import upload_youtube_video, get_youtube_handler
from .models import UploadedVideo, MatchupVideo
from ...forms import MyBaseModelForm
from ...utils import Map


class YoutubeUploadForm(forms.Form):
    token = forms.CharField()
    file = forms.FileField()


class MatchupVideoForm(MyBaseModelForm):
    file = forms.FileField(required=True)

    class Meta:
        model = MatchupVideo
        fields = ["title", "description"]

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        super(MatchupVideoForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(MatchupVideoForm, self).save(commit=False)
        cleaned_data = self.cleaned_data

        uploaded_video = UploadedVideo.objects.create(file_on_server=cleaned_data['file'])

        options = Map({
            "title": cleaned_data["title"],
            "description": cleaned_data["description"],
            "privacy": "public",
        })
        api = get_youtube_handler(options)

        video_id = upload_youtube_video(api, options, uploaded_video.file_on_server.path, 1, 1)
        instance.video_id = video_id
        instance.uploaded_by = self.request.user.profile
        instance.matchup = self.parent
        uploaded_video.delete()
        if commit:
            instance.save()
        return instance


