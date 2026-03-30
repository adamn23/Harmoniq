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

main module for Harmoniq.
Entry point for the Harmoniq song guessing game.
"""
from __future__ import annotations

import game_visualization
from SongGraph import SongGraph
from data_preprocessing import load_graph
from SongTree import SongTree
from question_state import QuestionState
from game_visualization import set_question_state
from input_bridge import answer_queue, start_console_input_thread, prompt_ready
import pandas as pd
import os
import pickle
import threading

GRAPH_CACHE = "song_graph_cache.pkl"
TREE_CACHE = "song_tree_cache.parquet"
MAX_GUESSES = 3


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

    Args:
        dataset_name: The name of the CSV file (without .csv extension).

    Returns:
        A cleaned DataFrame with one row per song, ready for SongTree.
    """
    if os.path.exists(TREE_CACHE):
        print("Loading song data from cache...")
        return pd.read_parquet(TREE_CACHE)

    print("Song data cache missing. Rebuilding...")
    _, df = load_graph(dataset_name, parquet_cache=TREE_CACHE)
    return df


def main() -> None:
    """Entry point for the Harmoniq song guessing game.

    Orchestrates the loading of data, the execution of the questioning loop,
    and the final guessing/verification phase.
    """
    df = get_cached_dataframe('spotify_dataset')
    graph = get_cached_graph('spotify_dataset')

    print("\nI am Harmoniq, the music genie.")
    print("Think of a song... but do NOT tell me.")
    print("I will peer into your mind and guess it.")
    print("\nReply only with: Yes / No / I don't know")

    # 1. Run the iterative tree search
    # final_state = run_guessing_loop(df)

    # 2. Handle the results (Success, Fallback, or Defeat)
    # handle_game_end(final_state, graph, df)

    backend_thread = threading.Thread(
        target=run_guessing_loop,
        args=(df, graph,),
        daemon=True
    )
    backend_thread.start()

    game_visualization.run_pygame()


def run_guessing_loop(df: pd.DataFrame, graph: SongGraph) -> SongTree:
    """Loop through questions until the SongTree reaches a leaf or empty state.
    Then go into the graph phase by calling handle_game_end() on graph

    Args:
        df: The DataFrame containing the current pool of possible songs.
        graph: The generated song graph

    Returns:
        The final SongTree state after the user has finished answering questions.
    """
    game_state = SongTree(df, set())

    # Begin an input thread for the game to wait for and fetch data from the console
    start_console_input_thread()

    # Pre-generate the first question so is_leaf() has data to look at
    game_state.update_split_scores()
    game_state.update_question()

    # Send data about the initial game/question state to pygame
    initial_question_state = QuestionState("", *game_state.get_question_data())
    game_visualization.set_question_state(initial_question_state)
    game_visualization.apply_question_state_visuals(initial_question_state)
    # game_visualization.run_pygame()
    # TODO: handle the multiple lines thing in the above initializer call

    # Asks the first question
    print(f"\n{game_state.get_question()}")
    print("> ", end="", flush=True)

    # Wait for and fetch first answer from answer queue
    prompt_ready.set()

    # Run the main game loop until we must return a guess
    while not game_state.is_leaf():
        answer, source = answer_queue.get()

        # adds the answer from pygame to console after the prompt arrow!
        print(f"\033[92m{answer}\033[0m \n", end="", flush=True) if source == 'pygame' else ...

        if answer in ["i don't know", "i dont know", "idk"]:
            answer = "i dont know"
        elif answer not in ['yes', 'no']:
            print("Please answer with Yes, No, or I don't know.")
            continue

        game_state = game_state.get_next_tree_state(answer)

        if game_state.is_leaf():
            game_visualization.ui_phase = "guessing"
            handle_game_end(game_state, graph, df)
            update_visualizer_state(game_state)
            break

        print(f"\n{game_state.get_question()}")
        print("> ", end="", flush=True)
        update_visualizer_state(game_state)
        prompt_ready.set()

    # Fetch and print final user input from pygame
    answer, source = answer_queue.get()
    print(f"\033[92m{answer}\033[0m \n", end="", flush=True) if source == 'pygame' else ...

    return game_state


def update_visualizer_state(game_state: SongTree) -> None:
    """
    Updates the game pygame visualization's current question state.
    """
    next_q_state = QuestionState('', *game_state.get_question_data())
    game_visualization.set_question_state(next_q_state)
    game_visualization.apply_question_state_visuals(next_q_state)


def handle_game_end(game_state: SongTree, graph: SongGraph, full_df: pd.DataFrame) -> None:
    """Final phase: Attempt to guess the song or admit defeat.

    Args:
        game_state: The final state of the SongTree.
        graph: The SongGraph used for similarity-based fallback guesses.
        full_df: The original, complete dataset for the final Akinator check.
    """
    pool = game_state.df

    if len(pool) == 0:
        print("\nMy logic has led me to a dead end... I have no guesses.")
        reveal_and_check_database(full_df)
        return

    # Identify the best primary guess (either the only song or the most popular one)
    if len(pool) == 1:
        best_guess = pool.iloc[0]
        print("\nI have narrowed it down to a single song!")
    else:
        best_guess = pool.loc[pool['popularity'].idxmax()]
        print(f"\nI have narrowed it down to {len(pool)} possibilities.")
        print("But I believe I know the answer.")

    print(f"Is it '{best_guess['song_name']}' by {best_guess['artists']}?")
    confirm = input("(Yes / No) > ").strip().lower()

    if confirm == "yes":
        print("Yes! I knew it.")
    else:
        conduct_fallback_guessing(game_state, graph, full_df, best_guess)


def conduct_fallback_guessing(game_state: SongTree, graph: SongGraph,
                              full_df: pd.DataFrame, first_guess: pd.Series) -> None:
    """Use graph similarity to make additional guesses before checking database.

    Args:
        game_state: The final SongTree state containing the remaining song pool.
        graph: The SongGraph used for similarity lookups.
        full_df: The complete dataset for the final Akinator check.
        first_guess: The first (incorrect) guess made by the engine.
    """
    print("Impressive... let me try using my intuition.")

    wrong_id = int(first_guess['song_id'])
    similar_songs = graph.get_similar(wrong_id, limit=20)
    current_pool_ids = set(game_state.df['song_id'])

    # Build and sort remaining candidates based on graph-similarity rank
    remaining_df = game_state.df[game_state.df['song_id'] != wrong_id]
    remaining = remaining_df.to_dict('records')

    sim_ids = [s.song_id for s in similar_songs if s.song_id in current_pool_ids]
    sim_rank = {s_id: i for i, s_id in enumerate(sim_ids)}
    remaining.sort(key=lambda r: sim_rank.get(int(r['song_id']), float('inf')))

    for i, candidate in enumerate(remaining):
        if i >= MAX_GUESSES:
            break

        print(f"Wait! Is it actually '{candidate['song_name']}' by {candidate['artists']}?")
        if input("(Yes / No) > ").strip().lower() == "yes":
            print("Aha! I knew I'd get there eventually.")
            return

    print("\nYou win this round. I am completely stumped!")
    reveal_and_check_database(full_df)


def reveal_and_check_database(df: pd.DataFrame) -> None:
    """The 'Akinator' check: Ask the user for the answer and verify against DB.

    Args:
        df: The full DataFrame to search for the user's song.
    """
    print("What was the song you were thinking of? (Enter in Console)")
    u_song = input("Song Name > ").strip()
    u_artist = input("Artist Name > ").strip()

    # Case-insensitive lookup in the full 500k dataset
    match = df[
        (df['song_name'].str.lower() == u_song.lower()) &
        (df['artists'].str.lower() == u_artist.lower())
        ]

    if not match.empty:
        actual = match.iloc[0]
        print(f"\nWait, '{actual['song_name']}' is in my database!")
        print("My algorithms failed me... I should have caught that.")
    else:
        print(f"\nI don't have '{u_song}' by {u_artist} in my records.")
        print("No wonder I couldn't guess it! You've beaten me fairly.")


if __name__ == '__main__':
    main()
