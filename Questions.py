"""
The module for the list of questions Harmoniq asks the user
"""

QUESTIONS: dict[str, str] = {

    # Boolean attributes
    "Is the song explicit?":                "explicit",
    "Is the song good for a party?":        "good_for_party",
    # "Is the song good for exercise?":       "good_for_exercise",
    "Is the song over {} minutes long?":    "length",
    "Is the song a collaboration?":         "is_collaboration",
    "Is the song a mainstream song?":       "is_mainstream",

    # Categorical attributes
    "Is the main genre {}?":                "primary_genre",
    "Is the emotion {}?":                   "emotion",

    # Artist / album attributes
    "Is the song by {}?":                   "artists",
    "Is the song from the album {}?":       "album",

    # Release date thresholds
    "Was the song released before {}?":     "release_date",
}
