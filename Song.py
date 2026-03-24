"""
Song module for Harmoniq.
Stores the data that each Song contains.
"""

from __future__ import annotations


class _Song:
    """A song vertex in the Harmonique song graph. Behaves like a weighted vertex.

    Instance Attributes:
        - song_id: Unique integer identifier for this song.
        - song_name: The name of the song.
        - artists: The artists credited on this song.
        - genre: The genre of the song.
        - emotion: The detected emotion of the song (e.g. 'sadness', 'joy').
        - tempo: Normalized tempo value (0.0–1.0).
        - energy: Energy level (0–100).
        - danceability: Danceability score (0–100).
        - popularity: Popularity score (0–100).
        - explicit: Whether the song contains explicit content.
        - good_for_party: Whether the song is good for a party.
        - good_for_work: Whether the song is good for work or study.
        - good_for_relaxation: Whether the song is good for relaxation or meditation.
        - good_for_exercise: Whether the song is good for exercise.

    Representation Invariants:
        - 0.0 <= tempo <= 1.0
        - 0 <= energy <= 100
        - 0 <= danceability <= 100
        - 0 <= popularity <= 100
    """

    # Private Instance Attributes:
    #   - _neighbours: a mapping from neighbouring songs
    #   to their similarity score to the current song (edge weights).

    song_id: int
    song_name: str
    artists: str
    genre: str
    emotion: str
    tempo: float
    energy: int
    danceability: int
    popularity: int
    release_date: str
    explicit: bool
    good_for_party: bool
    good_for_work: bool
    good_for_relaxation: bool
    good_for_exercise: bool
    _neighbours: dict[_Song, float]

    def __init__(self, song_id: int, song_name: str, artists: str,
                 genre: str, emotion: str, tempo: float,
                 energy: int, danceability: int, popularity: int,
                 explicit: bool, good_for_party: bool, good_for_work: bool,
                 good_for_relaxation: bool, good_for_exercise: bool,
                 release_date: str) -> None:
        """Initialize a _Song vertex with the given attributes.

        Args:
            song_id: Unique integer identifier for this song.
            song_name: The name of the song.
            artists: The artists credited on this song.
            genre: The genre of the song.
            emotion: The detected emotion of the song.
            tempo: Normalized tempo value (0.0–1.0).
            energy: Energy level (0–100).
            danceability: Danceability score (0–100).
            popularity: Popularity score (0–100).
            explicit: Whether the song contains explicit content.
            good_for_party: Whether the song is good for a party.
            good_for_work: Whether the song is good for work or study.
            good_for_relaxation: Whether the song is good for relaxation or meditation.
            good_for_exercise: Whether the song is good for exercise.
            release_date: The release date of the song
        """
        self.song_id = song_id
        self.song_name = song_name
        self.artists = artists
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
        self._neighbours = {}

    def add_neighbour(self, other: _Song, weight: float) -> None:
        """Add a neighbouring song with a similarity weight.

        Args:
            other: The neighbouring _Song vertex.
            weight: The similarity score between this song and other (0.0 to 1.0).

        Preconditions:
            - 0.0 <= weight <= 1.0
        """
        self._neighbours[other] = weight

    def get_neighbours(self) -> dict[_Song, float]:
        """Return a mapping of neighbouring songs to their similarity scores.

        Returns:
            A dict mapping each neighbouring _Song to its similarity weight.
        """
        return self._neighbours
