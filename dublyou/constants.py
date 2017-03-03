DEFAULT_INPUT_CLASSES = "form-control"

NAME_REGEX = r"^[-\s\.\w\d]{1,30}$"

INPUT_HTML_OUTPUT = """
                    <div class="input-group low-margin-vert">
                        %(errors)s
                        <span class="input-group-addon hidden-xs">
                            %(label)s
                        </span>
                        %(field)s
                    </div>"""

PLAYOFF_DI = {"name": "playoff_format",
              "fields": {
                  None: [],
                  1: ["playoff_bids"],
                  2: ["playoff_bids"],
                  3: ["playoff_bids"]
              }}

SEASON_TYPE_DI = {"name": "season_type",
                  "fields": {
                      1: ["rounds"],
                      2: ["season_games"]
                  }}

MATCHUP_TYPE_DI = {"name": "matchup_type",
                   "fields": {
                       1: [],
                       2: ["split_teams", "players_per_team"]
                   }}

COMPETITION_DI = {"name": "competition_type",
                  "fields": {
                      1: ["game"],
                      2: ["game", "series_games", "series_type"],
                      3: ["game", "tourney_type", "tourney_seeds"],
                      4: ["game", SEASON_TYPE_DI, PLAYOFF_DI],
                      5: []
                  }}

INPUT_CRITERIA = {
    "event_type": range(1, 5),
    "name": r"^[-\s\.\w\d]{1,30}$",
    "comp_type": range(1, 3),
    "players_per_team": range(2, 33),
    "split_teams": range(1, 3),
    "league": r"^[-\s\.\w\d]{1,30}$",
    "series_games": range(3, 16, 2),
    "tourney_type": range(1, 3),
    "tourney_seeds": range(1, 3),
    "season_scheduling_type": range(1, 3),
    "round_robin": range(1, 11),
    "season_games": range(2, 163, 2),
    "playoff_bids": range(2, 33),
    "playoff_format": [None, 1, 2, "series"],
    "num_events": range(2, 17),
    "game_rules": r"^[-\n\s\.\w\d]{1,300}$",
    "game_location": "^[-\s\.\w\d]{1,30}$",
}

PLAYERS_PER_TEAM = ((x, x) for x in INPUT_CRITERIA["players_per_team"])
SERIES_GAMES = ((x, x) for x in INPUT_CRITERIA["series_games"])
SEASON_GAMES = ((x, x) for x in INPUT_CRITERIA["season_games"])
PLAYOFF_BIDS = ((x, x) for x in INPUT_CRITERIA["playoff_bids"])

STATUS_TYPES = (
    (0, "incomplete"),
    (1, "upcoming"),
    (2, "dependency"),
    (3, "pending"),
    (4, "finished"),
    (5, "if necessary"),
    (6, "unnecessary"),
    (7, "deleted")
)

COMPETITION_TYPES = (
    (1, "matchup"),
    (2, "series"),
    (3, "tournament"),
    (4, "season"),
    (5, "olympics")
)

MATCHUP_TYPES = (
    (1, "individual"),
    (2, "team"),
)

RULE_TYPES = (
    (1, "scoring"),
    (2, "competitors"),
    (3, "other")
)

SPLIT_TEAMS = (
    (1, "manual"),
    (2, "random")
)

SERIES_TYPES = (
    (1, "best of"),
    (2, "first to"),
    (3, "play all")
)

TOURNEY_TYPES = (
    (1, "single elimination"),
    (2, "double elimination"),
    (3, "series best of")
)

TOURNEY_SEEDS = (
    (1, "random"),
    (2, "assigned")
)

SEASON_TYPES = (
    (1, "round robin"),
    (2, "games")
)

STATES = (
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "Dist of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
)

GAMES_CLASSES = (
    (1, "Sport"),
    (2, "Race"),
    (3, "Board Game"),
    (4, "Card Game"),
    (5, "Video Game"),
    (6, "Bar Game"),
    (7, "Other"),
)

SPORTS = (
    (1, "Basketball"),
    (2, "Badminton"),
    (3, "Volleyball"),
    (4, "Boxing"),
    (5, "Golf"),
    (6, "Hockey"),
    (7, "Football"),
    (8, "Soccer"),
    (9, "Swimming"),
    (10, "Tennis"),
    (11, "Table Tennis"),
    (12, "Other"),
    (13, "Baseball"),
    (14, "Bowling"),
    (15, "Darts"),
)

USER_NAVBAR = {
    "sections": [
        {"type": "reg",
         "classes": "",
         "members": [{"label": "Profile", "link": "/Profile/", "classes": ""}]
         },
        {"type": "button",
         "classes": "navbar-right med-margin-horz",
         "label": "Logout", "link": "/accounts/logout/"
         },
        {"type": "form",
         "classes": "navbar-right",
         "members": [{"type": "select",
                      "classes": "fit-width",
                      "id": "",
                      "placeholder": "Filter",
                      "options": [{"label": "Users", "value": "user"},
                                  {"label": "Teams", "value": "team"},
                                  {"label": "Leagues", "value": "league"},
                                  {"label": "Competitions", "value": "competitions"}
                                  ]
                      },
                     {"type": "text",
                      "classes": "",
                      "id": "user_search",
                      "placeholder": "Search"},
                     {"type": "submit",
                      "classes": "btn-primary",
                      "text": '<span class="glyphicon glyphicon-search" aria-hidden="true"></span>'}
                     ]
         }
    ]
}
