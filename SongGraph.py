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
        """Initialize an empty SongGraph."""
        self._songs = {}

    def add_song(self, song: _Song) -> None:
        """Add a song vertex to the graph.

        Args:
            song: The _Song vertex to add.

        Raises:
            ValueError: If a song with the same song_id already exists.
        """
        if song.song_id not in self._songs:
            self._songs[song.song_id] = song
        else:
            raise ValueError(f"Song with id {song.song_id} already exists.")

    def add_similarity(self, song_id1: int, song_id2: int, weight: float) -> None:
        """Add a weighted similarity edge between two songs.

        The edge is undirected: both song IDs are added to each other's neighbours.
        Does nothing if either song_id does not exist in the graph.

        Args:
            song_id1: The id of the first song.
            song_id2: The id of the second song.
            weight: The similarity score between the two songs (0.0 to 1.0).

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
        """Return the most similar songs to the given song, sorted by similarity score.

        Args:
            song_id: The id of the song to find neighbours for.
            limit: The maximum number of similar songs to return.

        Returns:
            A list of similar _Song vertices sorted by descending similarity score,
            or an empty list if the song does not exist.
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
        """Return the _Song vertex with the given song_id, or None if not found.

        Args:
            song_id: The id of the song to retrieve.

        Returns:
            The _Song vertex, or None if it does not exist.
        """
        return self._songs.get(song_id)

    def get_all_songs(self) -> list[_Song]:
        """Return all songs in the graph as a list.

        Returns:
            A list of all _Song vertices in the graph.
        """
        return list(self._songs.values())

    def __len__(self) -> int:
        """Return the number of songs in the graph.

        Returns:
            The number of _Song vertices in the graph.
        """
        return len(self._songs)

    def __contains__(self, song_id: int) -> bool:
        """Return whether a song with the given id exists in the graph.

        Args:
            song_id: The id to check.

        Returns:
            True if the song exists, False otherwise.
        """
        return song_id in self._songs
