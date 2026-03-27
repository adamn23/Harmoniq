"""
Song module for Harmoniq.
Defines the _Song class representing a single vertex in the SongGraph.
"""
from __future__ import annotations


class _Song:
    """A vertex representing a single song in the Harmoniq database.

    Instance Attributes:
        song_id: Unique integer ID for the song.
        song_name: The title of the song.
        artists: The artist(s) who created the song.
        album: The album the song belongs to.
        genre: The genre of the song.
        emotion: The emotional classification of the song.
        tempo: The BPM of the song.
        release_date: The release date as a string (YYYY-MM-DD).
        energy: Energy rating (0-100).
        danceability: Danceability rating (0-100).
        popularity: Spotify popularity score (0-100).
        explicit: Whether the song has explicit lyrics.
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
    good_for_morning: bool
    _neighbours: dict[int, float]

    def __init__(self, song_id: int, song_name: str, artists: str, album: str, genre: str,
                 emotion: str, tempo: float, release_date: str, energy: int,
                 danceability: int, popularity: int, explicit: bool, good_for_party: bool,
                 good_for_work: bool, good_for_relaxation: bool, good_for_exercise: bool,
                 good_for_running: bool, good_for_yoga: bool, good_for_driving: bool,
                 good_for_social: bool, good_for_morning: bool,
                 is_collaboration: bool, is_mainstream: bool) -> None:
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

        # Store IDs instead of object references to prevent RecursionError on pickling
        self._neighbours = {}

    def add_neighbour(self, song_id: int, weight: float) -> None:
        """Add a neighbouring song with a similarity weight.

        Args:
            song_id: The neighbouring _Song vertex.
            weight: The similarity score between this song and other (0.0 to 1.0).

        Preconditions:
            - 0.0 <= weight <= 1.0
        """
        self._neighbours[song_id] = weight

    def get_neighbours(self) -> dict[int, float]:
        """Return a mapping of neighbouring songs to their similarity scores.

        Returns:
            A dict mapping each neighbouring _Song to its similarity weight.
        """
        return self._neighbours
