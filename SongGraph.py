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

SongGraph module for Harmoniq.
This module defines the SongGraph class, a weighted graph ADT
representing similarity relationships between songs in the dataset.
"""

from __future__ import annotations

import doctest
from typing import Optional
from Song import _Song


class SongGraph:
    """A weighted graph representing similarity relationships between songs.

    Edges connect songs that appear in each other's 'Similar Songs' list,
    weighted by their similarity score.

    Instance Attributes:
        _songs: A dict mapping song_id to its corresponding _Song vertex.

    Representation Invariants:
        - All keys in _songs match the song_id of their corresponding _Song.
        - All edge weights are between 0.0 and 1.0.
    """

    _songs: dict[int, _Song]

    def __init__(self) -> None:
        """Initialize an empty SongGraph.
        """
        self._songs = {}

    def add_song(self, song: _Song) -> None:
        """Add a song vertex to the graph.

        Raises a ValueError if the song_id already exists in the graph.

        Preconditions:
            - song is a valid instance of _Song.

        Doctest Examples:
        >>> graph = SongGraph()
        >>> s = _Song(1, "Song A", "Artist A", "Album A", "Pop", "Happy", 0.5, "2020", 50, 50, 50,\
        False, False, False, False, False, False, False, False, False, False,\
        False, False, False, False, False, False, False, False, False, False)
        >>> graph.add_song(s)
        >>> 1 in graph
        True
        """
        if song.song_id not in self._songs:
            self._songs[song.song_id] = song
        else:
            raise ValueError(f"Song with id {song.song_id} already exists.")

    def add_similarity(self, song_id1: int, song_id2: int, weight: float) -> None:
        """Add an undirected weighted similarity edge between two songs.

        Does nothing if either song_id exists in the graph. Connects the two
        vertices by updating their respective internal neighbour dictionaries.

        Preconditions:
            - 0.0 <= weight <= 1.0
            - song_id1 != song_id2
        """
        if song_id1 not in self._songs or song_id2 not in self._songs:
            return

        song1 = self._songs[song_id1]
        song2 = self._songs[song_id2]

        # Pass the integer IDs rather than the song objects
        song1.add_neighbour(song_id2, weight)
        song2.add_neighbour(song_id1, weight)

    def get_similar(self, song_id: int, limit: int = 5) -> list[_Song]:
        """Return the most similar songs to the given song, sorted by similarity.

        Returns a list of _Song objects sorted by descending similarity score.
        If the song does not exist in the graph, returns an empty list.

        Preconditions:
            - limit > 0
        """
        if song_id not in self._songs:
            return []

        song = self._songs[song_id]

        # song.get_neighbours() now returns dict[int, float] (song_id -> weight)
        sorted_neighbours = sorted(
            song.get_neighbours().items(),
            key=lambda item: item[1],
            reverse=True
        )

        # Retrieve the actual _Song objects from the graph's dictionary using the IDs
        return [self._songs[neighbour_id] for neighbour_id, _ in sorted_neighbours[:limit]]

    def get_song(self, song_id: int) -> Optional[_Song]:
        """Return the _Song vertex with the given song_id.

        Returns None if the ID is not found in the graph.

        Preconditions:
            - song_id >= 0

        Doctest Examples:
        >>> graph = SongGraph()
        >>> graph.add_song(_Song(999, "Song A", "Artist A", "Album A", "Pop", "Happy", 0.5, "2020", 50, 50, 50,\
        False, False, False, False, False, False, False, False, False, False,\
        False, False, False, False, False, False, False, False, False, False))
        >>> graph.get_song(999) is None
        False
        """
        return self._songs.get(song_id)

    def get_all_songs(self) -> list[_Song]:
        """Return a list containing all _Song vertices in the graph.
        """
        return list(self._songs.values())

    def __len__(self) -> int:
        """Return the total number of songs (vertices) currently in the graph.
        """
        return len(self._songs)

    def __contains__(self, song_id: int) -> bool:
        """Check if a song with the given ID exists in the graph.

        Preconditions:
            - song_id >= 0
        """
        return song_id in self._songs


if __name__ == "__main__":
    import python_ta

    doctest.testmod()

    python_ta.check_all(config={
        'extra-imports': [
            'pandas', 'Song', 'SongGraph', 'CONSTANTS', 'rapidfuzz', 're', 'zlib'
        ],
        'allowed-io': ['process_csv', 'load_graph', 'enrich_with_musicbrainz'],
        'max-line-length': 120,
        'disable': ['R1705', 'C0200', 'W0401', 'C0325', 'R0915', 'C9104']
    })
