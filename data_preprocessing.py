"""
data_preprocessing module for Harmoniq.
Handles loading and preprocessing the dataset CSV into a SongGraph and DataFrame.
"""

from __future__ import annotations
import pandas as pd
from Song import _Song
from SongGraph import SongGraph

# Priority order for genre selection: more specific/niche genres beat generic ones.
# A song tagged "pop, rap, hip hop" will resolve to "hip hop" since it ranks highest.
# Pop is last because it is commonly added as a secondary tag to almost everything.
GENRE_PRIORITY = [
    'hip hop', 'rap', 'r&b', 'soul', 'jazz', 'blues', 'reggae', 'latin',
    'metal', 'rock', 'punk', 'indie', 'folk', 'country', 'classical',
    'electronic', 'dance', 'house', 'techno', 'edm', 'k-pop', 'pop'
]


def _pick_primary_genre(genre_str: str) -> str:
    """Pick the most specific genre from a comma-separated genre string.

    Iterates through GENRE_PRIORITY and returns the first tag that appears
    in the song's genre list. Falls back to the first tag if none match.

    Args:
        genre_str: A comma-separated string of genre tags (e.g. "pop, rap, hip hop").

    Returns:
        The single most representative genre tag for this song.
    """
    tags = [t.strip().lower() for t in genre_str.split(',')]
    for genre in GENRE_PRIORITY:
        if genre in tags:
            return genre
    return tags[0]


def process_csv(dataset_name: str) -> pd.DataFrame:
    """Load and preprocess the dataset CSV into a cleaned DataFrame.

    Performs column standardization, type conversion, derived feature
    creation, primary genre extraction, and deduplication.

    Args:
        dataset_name: The name of the CSV file (without .csv extension).

    Returns:
        A cleaned DataFrame with all columns correctly typed and duplicates removed.
    """
    df = pd.read_csv(dataset_name + '.csv')

    # Standardize column names: lowercase, replace spaces/slashes with underscores,
    # remove parentheses
    df.columns = [
        col.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
        for col in df.columns
    ]

    # Rename ambiguous column names to clearer ones
    if 'song' in df.columns:
        df.rename(columns={'song': 'song_name'}, inplace=True)
    if 'artist_s' in df.columns:
        df.rename(columns={'artist_s': 'artists'}, inplace=True)

    # Convert length from "MM:SS" string to total seconds
    df['length'] = (60 * df['length'].str.split(':').str[0].astype(int)
                    + df['length'].str.split(':').str[1].astype(int))

    # Derived boolean features
    df['is_collaboration'] = df['artists'].str.contains(',')
    df['is_mainstream'] = df['popularity'] >= 80

    df['release_date'] = pd.to_datetime(df['release_date'], format='mixed').dt.strftime('%Y-%m-%d')

    # Extract mode from key column then drop key
    if 'key' in df.columns:
        df['mode'] = df['key'].str.split(' ').str[1]
        df.drop(columns=['key'], inplace=True)

    df['loudness_db'] = df['loudness_db'].str.replace('db', '', regex=False).astype(float)
    df['explicit'] = df['explicit'].replace({'Yes': True, 'No': False})

    # Convert all good_for_* columns to bool
    for col in df.columns:
        if col.startswith('good_for'):
            df[col] = df[col].astype(bool)

    # Extract a single representative genre using the priority list.
    # e.g. "pop, rap, hip hop" -> "hip hop" since hip hop ranks above pop.
    df['primary_genre'] = df['genre'].apply(_pick_primary_genre)

    # Remove duplicate songs (same title + artist), keeping the first occurrence
    df = df.drop_duplicates(subset=['song_name', 'artists'], keep='first')

    return df


def load_graph(dataset_name: str, parquet_cache: str = "song_tree_cache.parquet") -> tuple[SongGraph, pd.DataFrame]:
    """Load the dataset and return a populated SongGraph and cleaned DataFrame.

    The DataFrame is saved to parquet immediately after preprocessing —
    before the graph build begins — so the SongTree cache is available
    as fast as possible on first run.

    Args:
        dataset_name: The name of the CSV file (without .csv extension).
        parquet_cache: Path to write the parquet cache file.

    Returns:
        A tuple of:
            - SongGraph with all songs added and similarity edges built.
            - Cleaned DataFrame with one row per song, ready for SongTree.
    """
    df = process_csv(dataset_name).reset_index(drop=True)
    df['song_id'] = df.index

    # Save the DataFrame cache immediately — don't wait for the slow graph build
    print("Saving song data cache...")
    df.to_parquet(parquet_cache, index=False)

    graph = SongGraph()
    rows = df.to_dict('records')

    # First pass: create all _Song objects and add them to the graph
    print("Building song graph...")
    songs = [
        _Song(
            song_id=song_id,
            song_name=row['song_name'],
            artists=row['artists'],
            album=row['album'],
            genre=row['genre'],
            emotion=row['emotion'],
            tempo=float(row['tempo']),
            release_date=row['release_date'],
            energy=int(row['energy']),
            danceability=int(row['danceability']),
            popularity=int(row['popularity']),
            explicit=bool(row['explicit']),
            good_for_party=bool(row['good_for_social_gatherings']),
            good_for_work=bool(row['good_for_work_study']),
            good_for_relaxation=bool(row['good_for_relaxation_meditation']),
            good_for_exercise=bool(row['good_for_exercise']),
            good_for_running=bool(row['good_for_running']),
            good_for_yoga=bool(row['good_for_yoga_stretching']),
            good_for_driving=bool(row['good_for_driving']),
            good_for_social=bool(row['good_for_social_gatherings']),
            good_for_morning=bool(row['good_for_morning_routine']),
            is_collaboration=bool(row['is_collaboration']),
            is_mainstream=bool(row['is_mainstream']),
        )
        for song_id, row in enumerate(rows)
    ]

    for song in songs:
        graph.add_song(song)

    # Build name -> song_id lookup for edge wiring
    name_artist_to_id = {(s.song_name, s.artists): s.song_id for s in songs}

    # Second pass: build similarity edges
    print("Building similarity edges...")
    for song_id, row in enumerate(rows):
        for i in range(1, 4):
            sim_name_key = f'similar_song_{i}'
            sim_artist_key = f'similar_artist_{i}'
            sim_score_key = f'similarity_score_{i}'

            similar_name = row.get(sim_name_key)
            similar_artist = row.get(sim_artist_key)
            similarity_score = row.get(sim_score_key)

            if pd.isna(similar_name) or pd.isna(similar_artist):
                continue

            neighbour_id = name_artist_to_id.get((similar_name, similar_artist))
            if neighbour_id is not None:
                graph.add_similarity(song_id, neighbour_id, float(similarity_score))

    return graph, df
