from __future__ import annotations

class _Song:
    """
    A class representing the data of Song in the Harmonique Song Tree. Behaves like a Weighted Vertex.

    Instance Attributes:
        - song_id: Unique Integer Identifier for the song represented by this _Song Vertex
        - song_name: The name of the song
        - artists: The artists credited on this song
    """
    # Private Instance Attributes:
    #   - _neighbours: a mapping from neighbouring songs
    #   to their similarity score to the current song (Edge Weights)
    song_id: int
    song_name: str
    artists: str

    _neighbours: dict[_Song, float]

class SongGraph:
    """
    Our implementation of the Graph ADT to represent the
    relationships between similar Songs in the dataset.
    """
