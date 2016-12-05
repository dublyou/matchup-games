DEFAULT_INPUT_CLASSES = "form-control"

INPUT_HTML_OUTPUT = '<div class="input-group low-margin-vert">%(errors)s<span class="input-group-addon hidden-xs">%(label)s</span> %(field)s</div>'

EVENT_TYPES = (
    (1, "showdown"),
    (2, "series"),
    (3, "tournament"),
    (4, "season"),
    (5, "olympics")
)

COMP_TYPES = (
    (1, "individual"),
    (2, "team"),
)

RULE_TYPES = (
    (1, "scoring"),
    (2, "other")
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