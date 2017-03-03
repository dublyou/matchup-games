from ...permissions import PermissionLogic, remove_items


class LeaguePermissions(PermissionLogic):
    owner = "commissioner"
    groups = ["players", "invitees"]
    allowable_actions = {
        "owner":
            ["edit_league", "delete_league", "new_competition",
             "league_invite", "manage_teams", "league_manage_players",
             "manage_league_signup", "approve_league_invite"],
        "players": ["league_withdraw"],
        "invitees": ["accept_league_invite"]
    }
    base_actions = ["view", "standings", "join_league",
                    "league_competitions", "league_signup"]

    permission_vars = ["status", "matchup_type"]

    def scrub(self):
        actions = super(LeaguePermissions, self).scrub()
        (status, matchup_type) = self.get_permission_vars()

        if matchup_type == 1:
            actions = remove_items(actions, ["add_team", "manage_teams"])

        return actions


class TeamPermissions(PermissionLogic):
    owner = "captain"
    groups = ["players", "league_players", "invitees"]
    allowable_actions = {
        "owner": ["edit_team", "team_manage_players", "team_invite", "drop_player", "join_team"],
        "invitees": ["join_team"]
    }
    base_actions = ["view", "team_upcoming_matchups", "team_matchup_results"]
    permission_vars = ["status"]

    def scrub(self):
        actions = super(TeamPermissions, self).scrub()

        return actions

