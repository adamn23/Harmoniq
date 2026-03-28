"""
The module for the list of questions Harmoniq asks the user
"""

QUESTIONS: dict[str, str] = {

    # Boolean attributes
    "Is the song explicit?":                "explicit",

    # "Is the song good for a party?":        "good_for_party",

    # "Is the song good for exercise?":     "good_for_exercise",

    "Is the song over {} minutes long?":    "length",

    "Is the song a collaboration?":         "is_collaboration",

    # "Is the song a mainstream song?":     "is_mainstream",

    "Is the song fast paced?":              "fast_paced",

    "Does the artist say the title "
    "of the song in the lyrics?":           "mentions_title",

    "Does the song ask a question "
    "in the lyrics?":                       "contains_question",

    "Does the song explore the theme of heartbreak or breakup?": "discusses_heartbreak",

    "Does the song talk about love or romance?": "discusses_love",

    "Does the song discuss money, wealth, or flexing?": "discusses_wealth",

    "Does the song explore the theme of religion or spirituality?": "discusses_religion",

    "Does the song talk about nightlife or partying?": "discusses_party",

    "Does the song explore the theme of sex or intimacy?": "discusses_intimacy",

    "Does the song discuss family, home, or childhood?": "discusses_family",

    "Does the song talk about hustle, ambition, or success?": "discusses_hustle",

    "Does the song explore the theme of struggle or hard times?": "discusses_struggle",

    "Does the song talk about confidence or empowerment?": "discusses_confidence",

    "Does the song discuss mental health?": "discusses_mental_health",

    "Does the song talk about violence, street life, or crime?": "discusses_violence",

    "Does the song explore politics or social issues?": "discusses_politics",

    "Does the song talk about good vibes?": "discusses_good_vibes",

    # --------------------------------------------------------

    # Categorical attributes
    "Is the main genre {}?":                "primary_genre",

    # "Is the emotion {}?":                   "emotion",

    "Is the song by {}?":                   "artists",

    "Is the song from the album {}?":       "album",

    "Was the song released before {}?":     "release_date",
}


MAIN_IDEA_QUESTIONS: dict[str, str] = {

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

}
