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

data_preprocessing module for Harmoniq.
Handles loading and preprocessing the dataset CSV into a SongGraph and DataFrame.
"""

from __future__ import annotations

import zlib
import pandas as pd
from Song import _Song
from SongGraph import SongGraph
from CONSTANTS import *
import re


def enrich_with_musicbrainz(df: pd.DataFrame, mb_cache: str = 'mb_artists.parquet') -> pd.DataFrame:
    """
    Get an updated DataFrame by combining song data with artists data
    :param df: The pandas DataFrame
    :param mb_cache: the path to the artists parquet
    :return: the updated DataFrame
    """
    mb = pd.read_parquet(mb_cache)[['artist_name', 'mb_type', 'mb_gender', 'country']]

    # Score each row so the best match wins when there are duplicates.
    # Lower score = better. Person > Group > others, known gender preferred,
    # known country preferred.
    mb['_score'] = (
            (mb['mb_type'] != 'Person').astype(int) * 10
            + mb['mb_gender'].isna().astype(int) * 3
            + mb['country'].isna().astype(int) * 1
    )
    mb = mb.sort_values('_score').drop_duplicates(subset='artist_name', keep='first')
    mb = mb.drop(columns='_score')

    df['primary_artist'] = df['artists'].str.split(',').str[0].str.strip()
    df = df.merge(mb, left_on='primary_artist', right_on='artist_name', how='left')
    df.drop(columns=['primary_artist', 'artist_name'], inplace=True)

    df['is_solo_artist'] = df['mb_type'] == 'Person'
    df['is_group'] = df['mb_type'] == 'Group'
    df['is_female_artist'] = df['mb_gender'] == 'Female'
    df['is_male_artist'] = df['mb_gender'] == 'Male'
    df['is_american_artist'] = df['country'] == 'US'
    df['is_british_artist'] = df['country'] == 'GB'
    df['is_canadian_artist'] = df['country'] == 'CA'
    df['is_european_artist'] = df['country'].isin({
        'DE', 'FR', 'SE', 'IT', 'ES', 'NL', 'NO', 'DK',
        'FI', 'BE', 'CH', 'AT', 'IE', 'PT', 'GR', 'PL'
    })

    match_rate = df['mb_type'].notna().mean()
    print(f"MusicBrainz match rate: {match_rate:.1%}")

    return df


def clean_text(text: str) -> str:
    """Removes punctuation and extra whitespace, converts to lowercase."""
    if not isinstance(text, str):
        return ""
    # Remove everything that isn't a letter or a number
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    # Collapse multiple spaces into one
    return " ".join(text.split())


def check_title_in_lyrics(row) -> bool:
    """Checks if the cleaned song title exists within the cleaned lyrics."""
    clean_title = clean_text(row['song_name'])
    clean_lyric = clean_text(row['text'])

    if not clean_title or not clean_lyric:
        return False

    return clean_title in clean_lyric


def add_main_ideas(df: pd.DataFrame) -> pd.DataFrame:
    """Classify each song into a single dominant topic bucket.

    Uses keyword density (hits per 100 words) rather than raw counts, so
    short and long songs are treated fairly. A song is only assigned a topic
    if one category clearly dominates — ambiguous songs fall to 'other'.

    Algorithm:
        1. Count keyword hits per topic using vectorized regex.
        2. Normalize by lyrics word count → density (hits per 100 words).
        3. Require density >= MIN_DENSITY (0.8) — filters songs with barely
           any matching words.
        4. Require winner density >= 1.5x runner-up density — filters songs
           where two topics score similarly (e.g. a love-and-heartbreak song).

    Args:
        df: The pandas DataFrame with a 'text' column of lyrics.

    Returns:
        The DataFrame with 'main_topic' and 'is_about_*' boolean columns added.
    """
    text_series = df['text'].fillna('').astype(str).str.lower()

    # Word count per song, clipped to 1 to avoid division by zero on empty lyrics
    word_counts = text_series.str.split().str.len().clip(lower=1)

    # Raw keyword hit counts per topic
    count_df = pd.DataFrame(index=df.index)
    for topic, regex in TOPIC_KEYWORDS.items():
        count_df[topic] = text_series.str.count(regex)

    # Normalize to hits-per-100-words so song length doesn't skew results
    density_df = count_df.div(word_counts, axis=0) * 100

    # Tentative winner: the topic with the highest density
    winner = density_df.idxmax(axis=1)
    max_density = density_df.max(axis=1)

    # Runner-up density: sort each row descending and pick index 1
    runner_up_density = density_df.apply(
        lambda row: row.sort_values(ascending=False).iloc[1], axis=1
    )

    # Dominance: winner must be at least 1.5x the runner-up
    # (if runner-up is 0, the winner dominates by definition)
    is_dominant = (runner_up_density == 0) | (max_density >= 1.5 * runner_up_density)

    df['main_topic'] = winner
    df.loc[max_density < MIN_DENSITY, 'main_topic'] = 'other'
    df.loc[~is_dominant, 'main_topic'] = 'other'

    for topic in TOPIC_KEYWORDS:
        df[f'is_about_{topic}'] = (df['main_topic'] == topic)

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

    # Lyrics-derived topic booleans
    df = add_main_ideas(df)

    # Structural / metadata booleans
    df['is_collaboration'] = df['artists'].str.contains(',')
    df['is_mainstream'] = df['popularity'] >= 80

    df['release_date'] = pd.to_datetime(df['release_date'], format='mixed').dt.strftime('%Y-%m-%d')

    # Extract mode from key column then drop key
    if 'key' in df.columns:
        df['mode'] = df['key'].str.split(' ').str[1]
        df.drop(columns=['key'], inplace=True)

    df['loudness_db'] = df['loudness_db'].str.replace('db', '', regex=False).astype(float)
    df['explicit'] = df['explicit'].replace({'Yes': True, 'No': False})

    # tempo is normalized 0.0–1.0 in this dataset; 0.6 ≈ upper-mid BPM range.
    # energy and danceability are 0–100 integer scores.
    df['fast_paced'] = df['tempo'] >= 0.6
    df['is_high_energy'] = df['energy'] >= 70
    df['is_danceable'] = df['danceability'] >= 60

    # Figure out emotion of song
    v = df['positiveness'] / 100
    e = df['energy'] / 100
    calc_joy = (v > 0.5) & (e > 0.4)
    calc_sadness = (v <= 0.5) & (e <= 0.6)

    # 3. Apply the flags using a hybrid approach
    # We prioritize the audio data but allow the label to act as a tie-breaker
    if 'emotion' in df.columns:
        low_emotion = df['emotion'].str.lower()

        # SADNESS: True if audio is low/low OR if label is sadness and energy isn't high
        df['is_sad_song'] = calc_sadness | (low_emotion == 'sadness')

        # JOY: True if audio is high/high. If audio is ambiguous, trust the 'joy' label.
        df['is_happy_song'] = calc_joy | ((low_emotion == 'joy') & (v > 0.4))

        # ANGER: True if audio is low valence/high energy.
        # Note: 'fear' in music often maps to high-tension/low-valence, similar to anger.
        df['is_angry_song'] = ((df['emotion'] == 'anger') &
                               (~df['is_sad_song']) &
                               (~df['is_happy_song']))

    # 4. Cleanup: Ensure a song isn't 'Sad' and 'Happy' at the same time
    # (Prioritize the audio-calculated sadness for Lana-style tracks)
    df.loc[df['is_sad_song'], 'is_happy_song'] = False
    df['mentions_title'] = df.apply(check_title_in_lyrics, axis=1)
    df['contains_question'] = df['text'].str.contains(r'\?', regex=True)

    # Convert all good_for_* columns to bool
    for col in df.columns:
        if col.startswith('good_for'):
            df[col] = df[col].astype(bool)

    # Extract a single representative genre using the priority list
    df['primary_genre'] = df['genre'].apply(_pick_primary_genre)

    text_lower = df['text'].fillna('').astype(str).str.lower()
    word_counts = text_lower.str.split().str.len().clip(lower=1)

    # 1. Is the song written in first person?
    #    Ratio of first-person pronouns to total words.
    #    Songs with very few "I/me/my" are third-person narratives or ambient/instrumental.
    first_person_counts = text_lower.str.count(r'\b(i|me|my|i\'m|i\'ve|i\'ll|i\'d|myself)\b')
    df['is_first_person'] = (first_person_counts / word_counts) >= 0.03  # 3+ per 100 words

    # 2. Does the song directly address "you"?
    #    Separates songs directed at a person ("I love you") from self-reflective ones.
    you_counts = text_lower.str.count(r'\b(you|your|you\'re|you\'ve|you\'ll|yourself)\b')
    df['addresses_you'] = (you_counts / word_counts) >= 0.02

    # 3. Does the song have a hook — a phrase repeated many times?
    #    Proxy: if the lyrics have low lexical diversity, there's heavy repetition.
    #    type-token ratio: unique words / total words. Low = repetitive/hook-heavy.
    def is_hook_heavy(text: str) -> bool:
        """
        Uses zlib compression ratio to detect high repetition (hooks).
        A lower ratio means more repetition.
        Standard Pop (like Britney/Drake) usually sits below 0.35 - 0.40.
        """
        if not isinstance(text, str) or len(text) < 50:
            return False

        # Encode to bytes for compression
        encoded_text = text.lower().encode('utf-8')
        compressed_size = len(zlib.compress(encoded_text))
        original_size = len(encoded_text)

        ratio = compressed_size / original_size

        # 0.40 is the sweet spot for songs like 'One Dance' or '...Baby One More Time'
        return ratio < COMPRESSION_RATIO

    df['has_hook'] = df['text'].fillna('').apply(is_hook_heavy)
    df['temp_song_clean'] = df['song_name'].astype(str).str.lower().str.strip()
    df['temp_artist_clean'] = df['artists'].astype(str).str.lower().str.strip()

    # Enrich with MusicBrainz artist metadata
    df = enrich_with_musicbrainz(df)

    # Remove duplicate songs (same title + artist), keeping the first occurrence
    df = df.drop_duplicates(subset=['song_name', 'artists'], keep='first')
    df = df.drop_duplicates(subset=['temp_song_clean', 'temp_artist_clean'], keep='first')
    df = df.drop(columns=['temp_song_clean', 'temp_artist_clean'])

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
