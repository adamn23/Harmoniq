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


def get_cached_graph(dataset_name: str, cache_file: str = "song_graph_cache.pkl") -> SongGraph:
    """Loads the graph from a cache if available, otherwise builds and caches it."""

    # Check if the cache file already exists
    if os.path.exists(cache_file):
        print("Summoning the music genie from cache...")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # If no cache exists, load it the hard way and then save it
    print("First run detected. Processing the song database...")
    graph = load_graph(dataset_name)

    print("Saving database to cache for future runs...")
    with open(cache_file, 'wb') as f:
        pickle.dump(graph, f)

    return graph


def main() -> None:
    """Run the Harmoniq song guessing game."""

    # Load the song data
    graph = get_cached_graph('spotify_dataset')
    all_songs = pd.Series(graph.get_all_songs())

    # Initialize the tree and compute the first question
    game_state = SongTree(all_songs, set())
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
    if len(game_state.songs) == 0:
        print("\nWell done, you have defeated me... for now.")
    elif len(game_state.songs) == 1:
        song = game_state.songs.iloc[0]
        print(f"\nI think your song is: '{song.song_name}' by {song.artists}!")
    else:
        print(f"I have narrowed it down to {len(game_state.songs)} possibilities...")
        most_popular = max(game_state.songs, key=lambda s: s.popularity)
        print("But I believe I know the answer.")
        print(f"Is it '{most_popular.song_name}' by {most_popular.artists}?")

        confirm = input("(Yes / No) > ").strip().lower()

        if confirm == "yes":
            print("Yes! I knew it.")
        else:
            print("Impressive... you got me this time.")


if __name__ == '__main__':
    main()
