from django.contrib.auth.mixins import LoginRequiredMixin

from . import models
from . import forms
from ...views import ProfileView, EditView, NewObjectView
from ...permissions import PermissionLogic


class GamePermissions(PermissionLogic):
    owner = "creator"
    groups = []
    allowable_actions = {
        "owner": ["edit_game"]
    }
    base_actions = ["view"]
    permission_vars = []


class NewGameView(LoginRequiredMixin, NewObjectView):
    form_title = "New Game"
    form_id = None
    form_action = None
    submit_label = "Create"
    form_class = forms.GameForm
    success_url = "/games/{id}/"

new_game = NewGameView.as_view()


class EditGameView(EditView):
    model = models.Game
    permission_logic = GamePermissions
    permission_required = "edit_game"
    login_required = True
    form_class = forms.GameForm
    form_title = "Edit Game"

edit_game = EditGameView.as_view()


class GameView(ProfileView):
    model = models.Game
    permission_logic = GamePermissions
    details = ["description", "game_type", "creator", "inventor"]
    stats = []
    tabs = []
    toolbar = [
        {"classes": "",
         "btns": [{"name": "edit_game",
                   "kwargs": {"pk": "instance__id"},
                   "glyph": "edit"}
                  ]
         }
    ]
