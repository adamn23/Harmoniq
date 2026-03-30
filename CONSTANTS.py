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

constants.py for Harmoniq.
Centralised constants shared across data_preprocessing, Song, and Questions.
"""

# ── Genre ─────────────────────────────────────────────────────────────────────

# Priority order for genre selection: more specific/niche genres beat generic ones.
# A song tagged "pop, rap, hip hop" will resolve to "hip hop" since it ranks highest.
# Pop is last because it is commonly added as a secondary tag to almost everything.
GENRE_PRIORITY: list[str] = [
    'hip hop', 'rap', 'r&b', 'soul', 'jazz', 'blues', 'reggae', 'latin',
    'metal', 'rock', 'punk', 'indie', 'folk', 'country', 'classical',
    'electronic', 'dance', 'house', 'techno', 'edm', 'k-pop', 'pop'
]

DANCEABLE_GENRES: set[str] = {'dance', 'electropop', 'edm', 'k-pop', 'house', 'electronic'}

# ── Lyric topic keywords ──────────────────────────────────────────────────────

# Keywords for each topic bucket.
# Words are chosen to be as mutually exclusive as possible; avoid terms that
# appear naturally in multiple categories (e.g. "heart", "pain", "baby").
MIN_DENSITY: float = 0.8
COMPRESSION_RATIO = 0.4

TOPIC_KEYWORDS: dict[str, str] = {
    'romance': r'\b(romance|romantic|kiss|kissing|kissed|darling|soulmate|'
               r'affection|loving|adore|adoring|cherish|sweetheart|'
               r'devotion|infatuation|falling in love|passion|beloved|'
               r'smitten|courtship|intimate|intimacy|valentine|amorous)\b',

    'heartbreak': r'\b(heartbreak|heartbroken|crying|cried|tears|tear-stained|'
                  r'lonely|loneliness|goodbye|breakup|broke up|'
                  r'regret|shattered|without you|miss you|missing you|'
                  r'left me|you left|moved on|heartache|weeping|unrequited|'
                  r'forsaken|sorrow|mourning|aching|dumped)\b',

    'hustle': r'\b(money|rich|wealth|success|winning|grind|hustle|'
              r'cash|bills|boss|fame|empire|luxury|'
              r'diamonds|chains|throne|making it|come up|stacks|'
              r'racks|commas|profit|mansion|thriving|bread|balling|'
              r'ambitious|revenue|fortune)\b',

    'partying': r'\b(club|clubbing|party|partying|drunk|drinking|'
                r'tonight|bottles|shots|celebrate|celebration|'
                r'turn up|nightlife|rager|hangover|wasted|'
                r'dancefloor|liquor|tequila|champagne|strobe|vip|'
                r'intoxicated|mixer)\b',

    'violence': r'\b(gun|guns|shoot|shooting|kill|killing|fight|fighting|'
                r'blood|war|warfare|murder|weapon|weapons|'
                r'blade|knife|gang|gangster|trigger|ammo|'
                r'bullet|glock|pistol|homicide|conflict|execution|'
                r'artillery|assault|rivals|opps)\b',
}

# ── Places (for mentions_place boolean) ───────────────────────────────────────

PLACES_REGEX: str = (
    r'\b(new york|new york city|nyc|brooklyn|bronx|harlem|queens|'
    r'los angeles|la|compton|watts|inglewood|'
    r'atlanta|chicago|houston|miami|detroit|'
    r'london|paris|tokyo|toronto|montreal|'
    r'california|texas|georgia|'
    r'the hood|the block|the streets|the south|the west|the east)\b'
)

# ── MusicBrainz country codes ─────────────────────────────────────────────────

EUROPEAN_COUNTRY_CODES: set[str] = {
    'DE', 'FR', 'SE', 'IT', 'ES', 'NL', 'NO', 'DK',
    'FI', 'BE', 'CH', 'AT', 'IE', 'PT', 'GR', 'PL'
}
