"""
The module for the list of questions Harmoniq asks the user
"""

QUESTIONS: dict[str, str] = {

    # Boolean attributes
    "Is the song explicit?":                "explicit",
    "Is the song good for a party?":        "good_for_party",
    "Is the song good for work?":           "good_for_work",
    "Is the song good for relaxation?":     "good_for_relaxation",
    "Is the song good for exercise?":       "good_for_exercise",
    "Is the song good for running?":        "good_for_running",
    "Is the song good for driving?":        "good_for_driving",
    "Is the song good for yoga?":           "good_for_yoga",
    "Is the song good for social events?":  "good_for_social",
    "Is the song good for mornings?":       "good_for_morning",

    # Categorical attributes
    "Is the genre {}?":                     "genre",
    "Is the emotion {}?":                   "emotion",

    # Artist / album attributes
    "Is the song by {}?":                   "artists",
    "Is the song from the album {}?":       "album",

    # Release date thresholds
    "Was the song released before {}?":     "release_date",
}

