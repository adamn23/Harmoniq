"""
data_preprocessing module for Harmoniq.
Handles loading and preprocessing the dataset CSV into a SongGraph.
"""

from __future__ import annotations
import pandas as pd
from Song import _Song
from SongGraph import SongGraph

NUMBER_OF_SONGS = 100000


def process_csv(dataset_name: str) -> pd.DataFrame:
    """Load and preprocess the dataset CSV into a cleaned DataFrame.

    Args:
        dataset_name: The name of the CSV file (without .csv extension).

    Returns:
        A cleaned DataFrame with all columns correctly typed.
    """
    df = pd.read_csv(dataset_name + '.csv')
    df = df.head(NUMBER_OF_SONGS)
    df['Length'] = (60 * df['Length'].str.split(':').str[0].astype(int)
                    + df['Length'].str.split(':').str[1].astype(int))
    df['Release Date'] = pd.to_datetime(df['Release Date'], format='mixed').dt.strftime('%Y-%m-%d')
    df['Mode'] = df['Key'].str.split(' ').str[1]
    df.drop(columns=['Key'], inplace=True)
    df['Loudness (db)'] = df['Loudness (db)'].str.replace('db', '', regex=False).astype(float)
    df['Explicit'] = df['Explicit'].replace({'Yes': True, 'No': False})
    df['Good for Party'] = df['Good for Party'].astype(bool)
    df['Good for Work/Study'] = df['Good for Work/Study'].astype(bool)
    df['Good for Relaxation/Meditation'] = df['Good for Relaxation/Meditation'].astype(bool)
    df['Good for Exercise'] = df['Good for Exercise'].astype(bool)
    df['Good for Running'] = df['Good for Running'].astype(bool)
    df['Good for Yoga/Stretching'] = df['Good for Yoga/Stretching'].astype(bool)
    df['Good for Driving'] = df['Good for Driving'].astype(bool)
    df['Good for Social Gatherings'] = df['Good for Social Gatherings'].astype(bool)
    df['Good for Morning Routine'] = df['Good for Morning Routine'].astype(bool)
    return df


def load_graph(dataset_name: str) -> SongGraph:
    """Load the dataset and return a populated SongGraph.

    Args:
        dataset_name: The name of the CSV file (without .csv extension).

    Returns:
        A SongGraph with all songs added and similarity edges built.
    """
    df = process_csv(dataset_name).reset_index(drop=True)
    graph = SongGraph()
    rows = df.to_dict('records')

    # First pass: create all _Song objects
    songs = [
        _Song(
            song_id=song_id,
            song_name=row['song'],
            artists=row['Artist(s)'],
            album=row['Album'],
            genre=row['Genre'],
            emotion=row['emotion'],
            tempo=float(row['Tempo']),
            release_date=row['Release Date'],
            energy=int(row['Energy']),
            danceability=int(row['Danceability']),
            popularity=int(row['Popularity']),
            explicit=bool(row['Explicit']),
            good_for_party=bool(row['Good for Party']),
            good_for_work=bool(row['Good for Work/Study']),
            good_for_relaxation=bool(row['Good for Relaxation/Meditation']),
            good_for_exercise=bool(row['Good for Exercise']),
            good_for_running=bool(row['Good for Running']),
            good_for_yoga=bool(row['Good for Yoga/Stretching']),
            good_for_driving=bool(row['Good for Driving']),
            good_for_social=bool(row['Good for Social Gatherings']),
            good_for_morning=bool(row['Good for Morning Routine']),
        )
        for song_id, row in enumerate(rows)
    ]

    for song in songs:
        graph.add_song(song)

    # Build name -> song_id lookup
    name_artist_to_id: dict[tuple[str, str], int] = {
        (s.song_name, s.artists): s.song_id for s in songs
    }

    # Second pass: build similarity edges
    for song_id, row in enumerate(rows):
        for i in range(1, 4):
            similar_name = row[f'Similar Song {i}']
            similar_artist = row[f'Similar Artist {i}']
            similarity_score = row[f'Similarity Score {i}']

            if pd.isna(similar_name) or pd.isna(similar_artist):
                continue

            neighbour_id = name_artist_to_id.get((similar_name, similar_artist))
            if neighbour_id is not None:
                graph.add_similarity(song_id, neighbour_id, float(similarity_score))

    return graph
