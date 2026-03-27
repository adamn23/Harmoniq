"""
main module for Harmoniq.
Entry point for the Harmoniq song guessing game.
"""
from __future__ import annotations

from SongGraph import SongGraph
from data_preprocessing import load_graph
from SongTree import SongTree
import pandas as pd
import os
import pickle

GRAPH_CACHE = "song_graph_cache.pkl"
TREE_CACHE = "song_tree_cache.parquet"


def get_cached_graph(dataset_name: str) -> SongGraph:
    """Load the SongGraph from a pickle cache, building it on first run.

    On first run, also triggers the parquet cache to be saved inside
    load_graph before the graph build begins, so tree startup is fast
    even if the graph build takes a while.

    Args:
        dataset_name: The name of the CSV file (without .csv extension).

    Returns:
        A fully populated SongGraph with similarity edges.
    """
    if os.path.exists(GRAPH_CACHE):
        print("Loading graph from cache...")
        with open(GRAPH_CACHE, 'rb') as f:
            return pickle.load(f)

    print("First run detected. Processing the song database...")
    graph, _ = load_graph(dataset_name, parquet_cache=TREE_CACHE)

    print("Saving graph cache for future runs...")
    with open(GRAPH_CACHE, 'wb') as f:
        pickle.dump(graph, f)

    return graph


def get_cached_dataframe(dataset_name: str) -> pd.DataFrame:
    """Load the song DataFrame from a parquet cache, building it on first run.

    Parquet is a columnar binary format; loading 500k rows takes under a
    second, far faster than unpickling _Song objects and converting them.
    On first run, this is saved as an early step inside load_graph so it
    is available immediately without waiting for the full graph build.

    Args:
        dataset_name: The name of the CSV file (without .csv extension).

    Returns:
        A cleaned DataFrame with one row per song, ready for SongTree.
    """
    if os.path.exists(TREE_CACHE):
        print("Loading song data from cache...")
        return pd.read_parquet(TREE_CACHE)

    # Fallback: parquet missing but graph cache exists (e.g. old install).
    # Rebuild the parquet without re-pickling the graph.
    print("Song data cache missing. Rebuilding...")
    _, df = load_graph(dataset_name, parquet_cache=TREE_CACHE)
    return df


def main() -> None:
    """Run the Harmoniq song guessing game."""

    # Graph is used for similarity lookups; df feeds the SongTree directly.
    # On first run, get_cached_graph triggers load_graph which saves the
    # parquet early, so get_cached_dataframe finds it instantly after.
    df = get_cached_dataframe('spotify_dataset')
    graph = get_cached_graph('spotify_dataset')

    # Initialize the tree and compute the first question
    game_state = SongTree(df, set())
    game_state.update_split_scores()
    game_state.update_question()

    print("\nI am Harmoniq, the music genie.")
    print("Think of a song... but do NOT tell me.")
    print("I will peer into your mind and guess it.")
    print("\nReply only with: Yes / No / I don't know\n")

    # Game loop
    while not game_state.is_leaf():
        print(f"\n{game_state.get_question()}")
        answer = input("> ").strip().lower()

        if answer not in ['yes', 'no', 'i dont know']:
            print("Please answer properly.")
            continue

        game_state = game_state.get_next_tree_state(answer)

    # Leaf reached: reveal the song
    if len(game_state.df) == 0:
        print("\nWell done, you have defeated me... for now.")

    elif len(game_state.df) == 1:
        song = game_state.df.iloc[0]
        print(f"\nI think your song is: '{song['song_name']}' by {song['artists']}!")

    else:
        print(f"I have narrowed it down to {len(game_state.df)} possibilities...")
        most_popular = game_state.df.loc[game_state.df['popularity'].idxmax()]
        print("But I believe I know the answer.")
        print(f"Is it '{most_popular['song_name']}' by {most_popular['artists']}?")
        confirm = input("(Yes / No) > ").strip().lower()

        if confirm == "yes":
            print("Yes! I knew it.")
        else:
            print("Impressive... let me try one last time using my intuition.")

            wrong_song_id = int(most_popular['song_id'])
            similar_songs = graph.get_similar(wrong_song_id, limit=20)
            current_pool_ids = set(game_state.df['song_id'])

            # Build a unified list of dicts for all remaining candidates
            remaining_df = game_state.df[game_state.df['song_id'] != wrong_song_id]
            remaining: list[dict] = remaining_df.to_dict('records')

            # Prefer similar songs first by moving them to the front
            similar_ids_in_pool = [
                s.song_id for s in similar_songs if s.song_id in current_pool_ids
            ]
            remaining.sort(key=lambda r: (0 if int(r['song_id']) in similar_ids_in_pool else 1))

            for candidate in remaining:
                print(f"Wait! Is it actually '{candidate['song_name']}' by {candidate['artists']}?")
                final_confirm = input("(Yes / No) > ").strip().lower()

                if final_confirm == "yes":
                    print("Aha! I knew I'd get there eventually.")
                    break
            else:
                print("You win this round. I'll update my algorithms.")


if __name__ == '__main__':
    main()
