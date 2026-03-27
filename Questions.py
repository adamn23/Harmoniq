"""
The module for the list of questions Harmoniq asks the user
"""

QUESTIONS: dict[str, str] = {

    # Boolean attributes
    "Is the song explicit?":                "explicit",

    "Is the song good for a party?":        "good_for_party",

    # "Is the song good for exercise?":     "good_for_exercise",

    "Is the song over {} minutes long?":    "length",

    "Is the song a collaboration?":         "is_collaboration",

    # "Is the song a mainstream song?":     "is_mainstream",

    "Is the song fast paced?":              "fast_paced",

    "Does the artist say the title "
    "of the song in the lyrics?":           "mentions_title",

    "Does the song ask a question "
    "in the lyrics?":                       "contains_question",

    "Is this primarily a love song"
    " or about romance?":                   "is_about_romance",

    "Is the song about a breakup "
    "or feeling heartbroken?":              "is_about_heartbreak",

    "Is this a 'hustle' song about "
    "success, money, or wealth?":           "is_about_hustle",

    "Is this a song about"
    "clubbing or a partying?":              "is_about_partying",

    "Does the song have aggressive "
    "or violent themes?":                   "is_about_violence",


    # --------------------------------------------------------

    # Categorical attributes
    "Is the main genre {}?":                "primary_genre",

    # "Is the emotion {}?":                   "emotion",

    "Is the song by {}?":                   "artists",

    "Is the song from the album {}?":       "album",

    "Was the song released before {}?":     "release_date",
}
