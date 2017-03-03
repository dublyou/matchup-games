# -*- coding: utf-8 -*-
from django.db import models


class MatchupManager(models.Manager):
    pass


class StatMemberManager(models.Manager):
    PARENT_TYPES = ["Competition", "Matchup", "Series", "Tournament",
                    "Season", "Olympics", "MatchupCompetitor"]
    CHILD_TYPES = ["Competitor", "PlayerProfile", "Team", "LeaguePlayer"]

    def get_stat_member(self, parent, child):
        parent_class = type(parent).__name__
        child_class = type(child).__name__
        parent_type = self.PARENT_TYPES.index(parent_class) if parent_class in self.PARENT_TYPES else None
        child_type = self.CHILD_TYPES.index(child_class) if child_class in self.CHILD_TYPES else None
        if child_type and parent_type:
            obj, created = self.get_or_create(parent_id=parent.id, parent_type=parent_type,
                                              child_id=child.id, child_type=child_type)
            return obj
        return False
