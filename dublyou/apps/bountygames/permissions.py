from ...permissions import PermissionLogic, remove_items


class CompetitionPermissions(PermissionLogic):
    owner = "creator"
    groups = ["players", "invitees"]
    allowable_actions = {
        "owner":
            ["create_matchups", "edit_competition", "delete_competition",
             "manage_competition_signup", "manage_events", "manage_competitors", "sign_up_requests",
             ],
        "players": ["competition_withdraw"],
        "invitees": ["accept_competition_invite"]
    }
    base_actions = ["view", "competition_standings", "competition_matchup_results", "join_competition",
                    "competition_upcoming_matchups", "competition_bracket", "competition_signup"]

    permission_vars = ["status", "competition_type", "matchup_type", "signup_page", "parent"]

    def scrub(self):
        actions = super(CompetitionPermissions, self).scrub()
        (status, competition_type,
         matchup_type, signup_page, parent) = self.get_permission_vars()

        if self.group == "players":
            actions = remove_items(actions, ["join_competition"])

        if status == 0:
            actions = remove_items(actions, ["competition_upcoming_matchups", "competition_bracket"])
        if status < 2:
            actions = remove_items(actions, ["competition_standings", "competition_matchup_results"])
        elif status == 3:
            actions = remove_items(actions, ["create_matchups", "manage_competition_signup", "edit_competition",
                                             "manage_events", "manage_competitors", "sign_up_requests"])
        elif status == 4:
            actions = remove_items(actions, ["competition_upcoming_matchups", "create_matchups", "manage_competition_signup",
                                             "edit_competition", "manage_events", "manage_competitors", "sign_up_requests"])
        if status > 2:
            actions = remove_items(actions, ["join_competition", "competition_withdraw", "competition_signup"])

        if competition_type != 5:
            actions = remove_items(actions, ["competitions", "manage_events"])
        if competition_type != 3:
            actions = remove_items(actions, ["competition_bracket"])

        if not signup_page:
            actions = remove_items(actions, ["competition_signup"])

        if parent:
            actions = remove_items(actions, ["manage_competitors", "manage_competition_signup", "competition_signup"])

        return actions


class MatchupPermissions(PermissionLogic):
    owner = "creator"
    groups = ["witness", "competitors", "competition_members"]
    allowable_actions = {
        "owner": ["edit_matchup", "manage_result"]
    }
    base_actions = ["view", "upload_matchup_video", "matchup_videos"]
    permission_vars = ["status"]

    def scrub(self):
        actions = super(MatchupPermissions, self).scrub()
        status = self.get_permission_vars()[0]

        if status > 1:
            actions = remove_items(actions, ["edit_matchup"])
        if status not in [1, 3]:
            actions = remove_items(actions, ["manage_result"])

        return actions


class CompetitorPermissions(PermissionLogic):
    owner = "captain"
    groups = ["players", "competition_players", "invitees"]
    allowable_actions = {
        "owner": ["edit_competitor", "competitor_manage_players"],
        "invitees": ["join_competitor"]
    }
    base_actions = ["view", "competitor_upcoming_matchups", "competitor_matchup_results"]
    permission_vars = ["status", "competitor_type"]

    def scrub(self):
        actions = super(CompetitorPermissions, self).scrub()
        status, competitor_type = self.get_permission_vars()

        if competitor_type != 2:
            actions = remove_items(actions, ["competitor_manage_players"])
        if status == 0:
            actions = ["view"]
        return actions

