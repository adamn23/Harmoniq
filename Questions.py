"""
Harmoniq - Song Guessing Engine

Copyright (c) 2026 Adam Ahmed, Omer Sheaffer. All rights reserved.

This software and all associated documentation files (the "Software") are the property of the copyright holder.
No part of this Software may be reproduced, transmitted, distributed, modified, or otherwise used, in whole or in part,
in any form or by any means, whether electronic, mechanical, photocopying, recording, or otherwise, without the prior
express written permission of the copyright holder.

The unauthorized use, copying, or distribution of this Software is strictly prohibited and may result in civil and/or
criminal penalties under applicable law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE
LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM,
OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

The module for the list of questions Harmoniq asks the user.

Every question here must be answerable by a person who knows a song well —
no internal dataset metrics, no thresholds the player would need to look up.

Questions are split into two dicts:
  - QUESTIONS: asked freely at any pool size.
  - ARTIST_QUESTIONS: only injected by SongTree when the pool is small enough
    to make artist-level questions meaningful (see ARTIST_QUESTION_POOL_THRESHOLD
    in SongTree.py). Keeping them separate prevents one-by-one artist enumeration.
"""

QUESTIONS: dict[str, str] = {

    # ── Boolean: lyrics content ───────────────────────────────────────────────

    "Is this primarily a love song or about romance?":      "is_about_romance",

    "Is the song about a breakup or heartbreak?":           "is_about_heartbreak",

    "Is this a 'hustle' song about success or money?":      "is_about_hustle",

    "Is this a song about clubbing or partying?":           "is_about_partying",

    "Does the song have aggressive or violent themes?":     "is_about_violence",

    "Does the artist say the title of the song "
    "in the lyrics?":                                       "mentions_title",

    "Does the song contain a question in the lyrics?":      "contains_question",

    "Is the song written from the singer's own"
    " perspective (first person)?":                         "is_first_person",

    "Does the song directly address another "
    "person (lots of 'you'/'your')?":                       "addresses_you",

    "Does the song repeat a short phrase or "
    "hook many times?":                                     "has_hook",

    # ── Boolean: sound and feel ───────────────────────────────────────────────

    "Is the song explicit?":                                "explicit",

    "Is it a fast-paced song?":                             "fast_paced",

    "Is it an intense, high-energy song?":                  "is_high_energy",

    "Is it a song you could easily dance to?":              "is_danceable",

    "Is it a widely known, mainstream song?":               "is_mainstream",

    # ── Boolean: emotion (only scored if column exists in df) ─────────────────

    "Is it a sad or melancholic song?":                     "is_sad_song",

    "Is it a happy or upbeat song?":                        "is_happy_song",

    "Does the song have an angry or aggressive tone?":      "is_angry_song",

    # ── Boolean: structure ────────────────────────────────────────────────────

    "Is the song a collaboration between multiple artists?": "is_collaboration",

    # ── Threshold-based (human-interpretable) ────────────────────────────────

    "Is the song over {} minutes long?":                    "length",

    "Was the song released before {}?":                     "release_date",

    # ── Fine-grained categorical (useful once pool is smaller) ───────────────

    "Is the main genre {}?":                                "primary_genre",

    "Is the song from the album {}?":                       "album",

    # ── Artist metadata (from MusicBrainz) ───────────────────────────────────

    "Is it a band or group?":                               "is_group",

    "Is the main artist female?":                           "is_female_artist",

    "Is the main artist male?":                             "is_male_artist",

    "Is the artist American?":                              "is_american_artist",

    "Is the artist British?":                               "is_british_artist",

    "Is the artist Canadian?":                              "is_canadian_artist",

    "Is the artist European (non-British)?":                "is_european_artist",
}

# Artist questions are kept separate so SongTree can gate them behind a
# minimum pool-size threshold, avoiding one-by-one artist enumeration.
ARTIST_QUESTIONS: dict[str, str] = {
    "Is the song by {}?":                                   "artists",
}
