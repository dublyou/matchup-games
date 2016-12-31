DEFAULT_INPUT_CLASSES = "form-control"

INPUT_HTML_OUTPUT = """
                    <div class="input-group low-margin-vert">
                        %(errors)s
                        <span class="input-group-addon hidden-xs">
                            %(label)s
                        </span>
                        %(field)s
                    </div>"""

STATUS_TYPES = (
    (0, "incomplete"),
    (1, "upcoming"),
    (2, "dependency"),
    (3, "in progress"),
    (4, "finished"),
    (5, "if necessary"),
    (6, "overdue"),
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
    (1, "random"),
    (2, "manual")
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
    (2, "input")
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
    "brand": "dublyou",
    "sections": [
        {"type": "reg",
         "classes": "",
         "members": [{"label": "Home", "link": "/home/", "classes": ""},
                     {"label": "Profile", "link": "/Profile/", "classes": ""}
                     ]
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
