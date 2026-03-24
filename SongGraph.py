"""
SongGraph module for Harmoniq.
This module defines the SongGraph class, a weighted graph ADT
representing similarity relationships between songs in the dataset.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
from Song import _Song


class SongGraph:
    """A weighted graph representing similarity relationships between songs.

    Edges connect songs that appear in each other's 'Similar Songs' list,
    weighted by their similarity score.

    Instance Attributes:
        - _songs: A Series mapping song_id (index) to its corresponding _Song vertex.

    Representation Invariants:
        - All index values in _songs match the song_id of their corresponding _Song.
        - All edge weights are between 0.0 and 1.0.
    """
    songs: pd.Series[_Song]

    def __init__(self):
        self._songs = pd.Series(dtype=object)

    def add_song(self, song: _Song) -> None:
        """Add a song vertex to the graph.

        Does nothing if a song with the same song_id already exists.

        Args:
            song: The _Song vertex to add.
        """
        if song.song_id not in self._songs.index:
            self._songs[song.song_id] = song
        else:
            raise ValueError

    def add_similarity(self, song_id1: int, song_id2: int, weight: float) -> None:
        """Add a weighted similarity edge between two songs.

        The edge is undirected: both songs are added to each other's neighbours.
        Does nothing if either song_id does not exist in the graph.

        Args:
            song_id1: The id of the first song.
            song_id2: The id of the second song.
            weight: The similarity score between the two songs (0.0 to 1.0).

        Preconditions:
            - 0.0 <= weight <= 1.0
            - song_id1 != song_id2
        """
        if song_id1 not in self._songs.index or song_id2 not in self._songs.index:
            return

        song1 = self._songs[song_id1]
        song2 = self._songs[song_id2]

        song1.add_neighbour(song2, weight)
        song2.add_neighbour(song1, weight)

    def get_similar(self, song_id: int, limit: int = 5) -> list[_Song]:
        """Return the most similar songs to the given song, sorted by similarity score.

        Args:
            song_id: The id of the song to find neighbours for.
            limit: The maximum number of similar songs to return.

        Returns:
            A list of similar _Song vertices sorted by descending similarity score,
            or an empty list if the song does not exist.
        """
        if song_id not in self._songs.index:
            return []

        song = self._songs[song_id]
        sorted_neighbours = sorted(
            song.get_neighbours().items(),
            key=lambda item: item[1],
            reverse=True
        )
        return [neighbour for neighbour, _ in sorted_neighbours[:limit]]

    def get_song(self, song_id: int) -> Optional[_Song]:
        """Return the _Song vertex with the given song_id, or None if not found.

        Args:
            song_id: The id of the song to retrieve.

        Returns:
            The _Song vertex, or None if it does not exist.
        """
        if song_id not in self._songs.index:
            return None
        return self._songs[song_id]

    def get_all_songs(self) -> list[_Song]:
        """Return all songs in the graph as a list.

        Returns:
            A list of all _Song vertices in the graph.
        """
        return self._songs.tolist()

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
        return song_id in self._songs.index

