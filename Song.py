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

Song module for Harmoniq.
Defines the _Song class representing a single vertex in the SongGraph.
"""
from __future__ import annotations


class _Song:
    """A vertex representing a single song in the Harmoniq database.

    Instance Attributes:
        song_id: Unique integer identifier for this song.
        song_name: The name of the song.
        artists: The artists credited on this song.
        album: The album the song belongs to.
        genre: The genre of the song.
        emotion: The detected emotion of the song.
        tempo: Normalized tempo value (0.0–1.0).
        release_date: The release date of the song.
        energy: Energy level (0–100).
        danceability: Danceability score (0–100).
        popularity: Popularity score (0–100).
        explicit: Whether the song contains explicit content.
        fast_paced: Whether the song has a fast tempo or rhythm.
        good_for_party: Whether the song is good for a party.
        good_for_work: Whether the song is good for work or study.
        good_for_relaxation: Whether the song is good for relaxation or meditation.
        good_for_exercise: Whether the song is good for general exercise.
        good_for_running: Whether the song is good for running.
        good_for_yoga: Whether the song is good for yoga.
        good_for_driving: Whether the song is good for driving.
        good_for_social: Whether the song is good for social gatherings.
        is_mainstream: Whether the song is considered mainstream/popular.
        is_collaboration: Whether the song is a collaboration between artists.
        is_about_romance: Whether the song's lyrics focus on romance.
        is_about_heartbreak: Whether the song's lyrics focus on heartbreak.
        is_about_hustle: Whether the song is about ambition or work.
        is_about_partying: Whether the song is about partying.
        is_about_violence: Whether the song contains themes of violence.
        good_for_morning: Whether the song is suitable for listening in the morning.
        mentions_title: Whether the song lyrics mention the song title.
        contains_question: Whether the song lyrics include a question.
        _neighbours: A dictionary mapping neighbour song_ids (int) to similarity scores (float).
    """

    song_id: int
    song_name: str
    artists: str
    album: str
    genre: str
    emotion: str
    tempo: float
    release_date: str
    energy: int
    danceability: int
    popularity: int
    explicit: bool
    fast_paced: bool
    good_for_party: bool
    good_for_work: bool
    good_for_relaxation: bool
    good_for_exercise: bool
    good_for_running: bool
    good_for_yoga: bool
    good_for_driving: bool
    good_for_social: bool
    is_mainstream: bool
    is_collaboration: bool
    is_about_romance: bool
    is_about_heartbreak: bool
    is_about_hustle: bool
    is_about_partying: bool
    is_about_violence: bool
    good_for_morning: bool
    mentions_title: bool
    contains_question: bool
    _neighbours: dict[int, float]

    def __init__(self, song_id: int, song_name: str, artists: str, album: str, genre: str,
                 emotion: str, tempo: float, release_date: str, energy: int,
                 danceability: int, popularity: int, explicit: bool, good_for_party: bool,
                 good_for_work: bool, good_for_relaxation: bool, good_for_exercise: bool,
                 good_for_running: bool, good_for_yoga: bool, good_for_driving: bool,
                 good_for_social: bool, good_for_morning: bool,
                 is_collaboration: bool, is_mainstream: bool, fast_paced: bool,
                 mentions_title: bool, contains_question: bool,
                 is_about_romance: bool, is_about_heartbreak: bool, is_about_hustle: bool,
                 is_about_partying: bool, is_about_violence: bool) -> None:
        """Initialize a _Song vertex with the given attributes.

        Stores all metadata associated with a song and initializes an empty
        adjacency dictionary for the graph.

        Preconditions:
            - song_id >= 0
            - 0.0 <= tempo <= 1.0
        """
        self.song_id = song_id
        self.song_name = song_name
        self.artists = artists
        self.album = album
        self.genre = genre
        self.emotion = emotion
        self.tempo = tempo
        self.release_date = release_date
        self.energy = energy
        self.danceability = danceability
        self.popularity = popularity
        self.explicit = explicit
        self.good_for_party = good_for_party
        self.good_for_work = good_for_work
        self.good_for_relaxation = good_for_relaxation
        self.good_for_exercise = good_for_exercise
        self.good_for_running = good_for_running
        self.good_for_yoga = good_for_yoga
        self.good_for_driving = good_for_driving
        self.good_for_social = good_for_social
        self.is_mainstream = is_mainstream
        self.is_collaboration = is_collaboration
        self.good_for_morning = good_for_morning
        self.fast_paced = fast_paced
        self.mentions_title = mentions_title
        self.contains_question = contains_question
        self.is_about_violence = is_about_violence
        self.is_about_hustle = is_about_hustle
        self.is_about_romance = is_about_romance
        self.is_about_heartbreak = is_about_heartbreak
        self.is_about_partying = is_about_partying
        self._neighbours = {}

    def add_neighbour(self, song_id: int, weight: float) -> None:
        """Add a neighbouring song with the given similarity weight.

        Preconditions:
            - 0.0 <= weight <= 1.0
            - song_id >= 0

        Doctest Examples:
        >>> s = _Song(1, "A", "B", "C", "D", "E", 0.5, "F", 1, 1, 1,
        False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False, False, False)
        >>> s.add_neighbour(2, 0.85)
        >>> s.get_neighbours()
        {2: 0.85}
        """
        self._neighbours[song_id] = weight

    def get_neighbours(self) -> dict[int, float]:
        """Return a mapping of neighbouring songs to their similarity scores.

        Preconditions:
            - None

        Doctest Examples:
        >>> s = _Song(1, "A", "B", "C", "D", "E", 0.5, "F", 1, 1, 1,
        False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False, False, False)
        >>> s.add_neighbour(5, 0.9)
        >>> s.get_neighbours()
        {5: 0.9}
        """
        return self._neighbours


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [
            'pandas', 'Song', 'SongGraph', 'CONSTANTS', 'rapidfuzz', 're', 'zlib'
        ],
        'allowed-io': ['process_csv', 'load_graph', 'enrich_with_musicbrainz'],
        'max-line-length': 120,
        'disable': ['R1705', 'C0200', 'W0401', 'C0325', 'R0915']
        # R0915 disabled because process_csv exceeds it, but it would not make sense to split it up
    })
