from ...permissions import PermissionLogic, remove_items


class ProfilePermissions(PermissionLogic):
    owner = "user"
    profile = None
    groups = ["friends"]
    allowable_actions = {
        "owner": ["edit_profile", "new_competition", "new_league", "new_game", "send-invite",
                  "upcoming_matchups", "matchup_results", "my_competitions", "player_invitations"],
        "friends": ["send_message"]
    }
    base_actions = ["view", "add_friend"]
    permission_vars = []

    def scrub(self):
        actions = super(ProfilePermissions, self).scrub()
        if self.group != "anonymous":
            actions = remove_items(actions, ["add_friend"])
        return actions

