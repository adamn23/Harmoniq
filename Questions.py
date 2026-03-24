"""
The module for the list of questions Harmoniq asks the user
"""

QUESTIONS: dict[str, str] = {
    "Is the song good for a party?":        "good_for_party",
    "Is the song good for relaxation?":     "good_for_relaxation",
    "Is the song explicit?":                "explicit",
    "Is the genre hip hop?":                "genre",
    "Is the genre pop?":                    "genre",
    "Is the genre country?":                "genre",
    "Is the song sad?":                     "emotion",
    "Is the song angry?":                   "emotion",
    "Was the song released before {}?":     "release_date",
}

#  Non-boolean attributes:
#    * Categorical: Genre, Emotion
#    * Numerical: Release Date, Length
