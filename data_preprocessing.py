"""
data_preprocessing module for Harmoniq.
Handles loading and preprocessing the dataset CSV into a SongGraph and DataFrame.
"""

from __future__ import annotations
import pandas as pd
from Song import _Song
from SongGraph import SongGraph

from CONSTANTS import GENRE_PRIORITY, IDEA_MAP, TOPIC_KEYWORDS


def add_main_ideas(df: pd.DataFrame, count_cap: int = 3) -> pd.DataFrame:
    """
    Runs through IDEA_MAP, which orders keywords based off of priority.
    If a song hits multiple, the one higher in this dict wins.
    :param df: The pandas DataFrame
    :return:
    """

    text_series = df['text'].fillna('').astype(str).str.lower()

    # Store counts for each category
    count_df = pd.DataFrame(index=df.index)
    for topic, regex in IDEA_MAP.items():
        count_df[topic] = text_series.str.count(regex)

    # 2. Determine the "Winner"
    # idxmax returns the column name with the highest value for each row.
    # We only count it if the highest count is at least count_cap.
    df['main_topic'] = count_df.idxmax(axis=1)
    df.loc[count_df.max(axis=1) < count_cap, 'main_topic'] = 'other'

    # 3. Create the final booleans for your Song objects based on the winner
    for topic in IDEA_MAP.keys():
        df[f'is_about_{topic}'] = (df['main_topic'] == topic)

    return df


def add_topics_present(df: pd.DataFrame, min_hits: int = 3) -> pd.DataFrame:
    """
    Verify whether the song discusses topic_name based off whether at least a minimum amount
    (min_hits) of keywords are present in its lyrics.
    """
    text_series = df["text"].fillna("").astype(str).str.lower()

    for topic, regex in TOPIC_KEYWORDS.items():
        hits = text_series.str.count(regex)  # counts how many times any of the keywords are found in lyrics
        df[f"discusses_{topic}"] = (hits >= min_hits)
        # If we switch to a probability-based model this would be handy:
        # df[f"{topic}_hits"] = hits

    return df


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
    """Process and load the song dataset into a readable DataFrame object.
    TODO: remove or keep & implement: Use the help of an artist dataset to cross reference for extra questions.

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
    df = add_topics_present(df)
    df['is_collaboration'] = df['artists'].str.contains(',')
    df['is_mainstream'] = df['popularity'] >= 80

    df['release_date'] = pd.to_datetime(df['release_date'], format='mixed').dt.strftime('%Y-%m-%d')

    # Extract mode from key column then drop key
    if 'key' in df.columns:
        df['mode'] = df['key'].str.split(' ').str[1]
        df.drop(columns=['key'], inplace=True)

    df['loudness_db'] = df['loudness_db'].str.replace('db', '', regex=False).astype(float)
    df['explicit'] = df['explicit'].replace({'Yes': True, 'No': False})
    df['fast_paced'] = df['energy'] >= 120
    df['mentions_title'] = df.apply(lambda row: str(row['song_name']).lower() in str(row['text']).lower(), axis=1)
    df['contains_question'] = df['text'].str.contains(r'\?', regex=True)

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
            fast_paced=bool(row['fast_paced']),
            mentions_title=bool(row['mentions_title']),
            contains_question=bool(row['contains_question']),
            is_about_romance=bool(row['is_about_romance']),
            is_about_heartbreak=bool(row['is_about_heartbreak']),
            is_about_hustle=bool(row['is_about_hustle']),
            is_about_partying=bool(row['is_about_partying']),
            is_about_violence=bool(row['is_about_violence']),
            discusses_heartbreak=bool(row['discusses_heartbreak']),
            discusses_love=bool(row['discusses_love']),
            discusses_religion=bool(row['discusses_religion']),
            discusses_wealth=bool(row['discusses_wealth']),
            discusses_party=bool(row['discusses_party']),
            discusses_intimacy=bool(row['discusses_intimacy']),
            discusses_friendship=bool(row['discusses_friendship']),
            discusses_family=bool(row['discusses_family']),
            discusses_hustle=bool(row['discusses_hustle']),
            discusses_struggle=bool(row['discusses_struggle']),
            discusses_confidence=bool(row['discusses_confidence']),
            discusses_mental_health=bool(row['discusses_mental_health']),
            discusses_violence=bool(row['discusses_violence']),
            discusses_politics=bool(row['discusses_politics']),
            discusses_good_vibes=bool(row['discusses_good_vibes']),
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
