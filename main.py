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

import os
import pickle
import threading

import pandas as pd
import game_visualization
from SongGraph import SongGraph
from data_preprocessing import load_graph
from SongTree import SongTree
from question_state import QuestionState
from input_bridge import ANSWER_QUEUE, set_allow_text, start_console_input_thread, PROMPT_READY

GRAPH_CACHE = "song_graph_cache.pkl"
TREE_CACHE = "song_tree_cache.parquet"
MAX_GUESSES = 3


def get_cached_graph(dataset_name: str) -> SongGraph:
    """Load the SongGraph from a pickle cache, building it on first run.

    Checks for an existing serialized graph. If missing, it builds the graph,
    saves it to disk, and triggers the DataFrame parquet cache.

    Preconditions:
        - dataset_name corresponds to a valid base CSV file.
    """
    if os.path.exists(GRAPH_CACHE):
        print("Loading graph from cache...\n")
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

    Provides a cleaned DataFrame representing the database for the SongTree.

    Preconditions:
        - dataset_name corresponds to a valid base CSV file.
    """
    if os.path.exists(TREE_CACHE):
        print("Loading song data from cache...")
        return pd.read_parquet(TREE_CACHE)

    print("Song data cache missing. Rebuilding...")
    _, df = load_graph(dataset_name, parquet_cache=TREE_CACHE)
    return df


def get_text_input(prompt_text: str) -> str:
    """
    Wait for input from the Pygame ANSWER_QUEUE.
    Returns the first value received.

    Preconditions:
        - ANSWER_QUEUE contains tuples of the form (str, Any)
    """
    # 1. Print the prompt to the terminal so the console user knows what to type
    print(f"{prompt_text} > ", end="", flush=True)

    # 2. Signal the background console thread that we are ready for a terminal input
    # Allow the user to give text input
    set_allow_text(True)
    PROMPT_READY.set()

    # 3. Wait for the next item in the queue (blocks until either source puts data in)
    # This returns a tuple: (the_text_string, source_name)
    val, source = ANSWER_QUEUE.get()
    set_allow_text(False)
    # 4. If the input came from Pygame, mirror it to the console in green
    # so the terminal history stays complete
    if source == 'pygame':
        print(f"\033[92m{val}\033[0m")
    return val


def harmonique_say(text: str) -> None:
    """Print dialogue to the console and queue it in the Pygame visualizer.
    """
    print(text)
    game_visualization.queue_dialogue_text(text)


def main() -> None:
    """Entry point for the Harmoniq game.

    Loads data, starts the backend questioning thread, and launches the Pygame UI.

    Preconditions:
        - Required datasets/caches are available in the directory.
    """
    df = get_cached_dataframe('spotify_dataset')
    graph = get_cached_graph('spotify_dataset')

    harmonique_say("I am Harmoniq, the music genie.")
    harmonique_say("Think of a song... but do NOT tell me.")
    harmonique_say("I will peer into your mind and guess it.")

    # Dialogue only necessary in console, because pygame already only has these options.
    print("\nReply only with: Yes / No / I don't know")

    # Run the iterative tree search and recieve feedback.
    backend_thread = threading.Thread(
        target=run_guessing_loop,
        args=(df, graph,),
        daemon=True
    )
    backend_thread.start()

    game_visualization.run_pygame()


def run_guessing_loop(df: pd.DataFrame, graph: SongGraph) -> SongTree:
    """Loop through questions until the SongTree reaches a leaf or empty state.

    Interacts with the answer queue and progressively filters the DataFrame.

    Preconditions:
        - len(df) > 0
        - graph is populated
    """
    game_state = SongTree(df, set())

    # Begin an input thread for the game to wait for and fetch data from the console
    start_console_input_thread()

    # Pre-generate the first question so is_leaf() has data to look at
    game_state.update_split_scores()
    game_state.update_question()

    # Send data about the initial game/question state to pygame
    initial_question_state = QuestionState(*game_state.get_question_data())
    game_visualization.set_question_state(initial_question_state)
    game_visualization.apply_question_state_visuals(initial_question_state)
    # game_visualization.run_pygame()

    # Asks the first question
    print(f"\n{game_state.get_question()}")
    print("> ", end="", flush=True)

    # Wait for and fetch first answer from answer queue
    PROMPT_READY.set()

    # Run the main game loop until we must return a guess
    while not game_state.is_leaf():
        answer, source = ANSWER_QUEUE.get()

        # adds the answer from pygame to console after the prompt arrow!
        if source == 'pygame':
            print(f"\033[92m{answer}\033[0m \n", end="", flush=True)

        if answer in ["i don't know", "i dont know", "idk"]:
            answer = "i dont know"
        elif answer not in ['yes', 'no']:
            print("Please answer with Yes, No, or I don't know.")
            continue

        game_state = game_state.get_next_tree_state(answer)

        if game_state.is_leaf():
            # Handle the results (Success, Fallback, or Defeat)
            game_visualization.ui_phase = "guessing"
            handle_game_end(game_state, graph, df)
            break

        print(f"\n{game_state.get_question()}")
        print("> ", end="", flush=True)
        update_visualizer_state(game_state)
        PROMPT_READY.set()

    return game_state


def update_visualizer_state(game_state: SongTree) -> None:
    """Update the game pygame visualization's current question state.

    Extracts data from the current tree node and passes it to the Pygame UI.
    """
    next_q_state = QuestionState(*game_state.get_question_data())
    game_visualization.set_question_state(next_q_state)


def handle_game_end(game_state: SongTree, graph: SongGraph, full_df: pd.DataFrame) -> None:
    """Attempt to guess the song or admit defeat at the end of the tree phase.

    Makes a primary guess based on popularity, falling back to graph similarity
    if the primary guess is incorrect.

    Preconditions:
        - game_state.is_leaf() is True
    """
    pool = game_state.df

    if len(pool) == 0:
        game_visualization.initiate_final_result(False,
                                                 "My logic has led me to a dead end... I have no guesses.")
        harmonique_say("\nMy logic has led me to a dead end... I have no guesses.")
        reveal_and_check_database(full_df)
        return

    # Identify the best primary guess (either the only song or the most popular one)
    if len(pool) == 1:
        best_guess = pool.iloc[0]
        harmonique_say("\nI have narrowed it down to a single song!")
    else:
        best_guess = pool.loc[pool['popularity'].idxmax()]
        harmonique_say(f"\nI have narrowed it down to {len(pool)} possibilities.")
        harmonique_say("But I believe I know the answer.")

    game_visualization.ui_phase = "guessing"
    game_visualization.apply_guess_state(f"'{best_guess['song_name']}' by {best_guess['artists']}?")

    print(f"Is it '{best_guess['song_name']}' by {best_guess['artists']}?")

    print("(Yes / No) > ", end="", flush=True)
    PROMPT_READY.set()
    confirm, source = ANSWER_QUEUE.get()
    if source == 'pygame':
        print(f"\033[92m{confirm}\033[0m \n", end="", flush=True)
    confirm = confirm.strip().lower()

    if confirm == "yes":
        game_visualization.initiate_final_result(True,
                                                 f"'{best_guess['song_name']}' by {best_guess['artists']}")
        harmonique_say("Yes! I knew it.")
        harmonique_say("Restart the program to play another round!")
    else:
        conduct_fallback_guessing(game_state, graph, full_df, best_guess)


def conduct_fallback_guessing(game_state: SongTree, graph: SongGraph,
                              full_df: pd.DataFrame, first_guess: pd.Series) -> None:
    """Use graph similarity to make additional guesses before checking database.

    Fetches similar songs using the incorrect first guess, checks if they remain
    in the active pool, and asks the user up to MAX_GUESSES.

    Preconditions:
        - first_guess represents a valid song row in the dataframe.
    """
    harmonique_say("Impressive... let me try using my intuition.")

    wrong_id = int(first_guess['song_id'])

    # Get similar song IDs from the graph, in order of similarity score
    similar_song_objects = graph.get_similar(wrong_id, limit=20)
    similar_ids_ordered = [s.song_id for s in similar_song_objects]

    # Remaining pool excluding the wrong guess
    remaining_df = game_state.df[game_state.df['song_id'] != wrong_id].copy()
    pool_ids = set(remaining_df['song_id'].astype(int))

    # Filter similar_ids to only those actually in the remaining pool
    similar_ids_in_pool = [sid for sid in similar_ids_ordered if sid in pool_ids]

    # Build final candidate order:
    # 1. Graph-similar songs first (in similarity order)
    # 2. Then remaining pool songs by popularity
    similar_rows = remaining_df[remaining_df['song_id'].isin(similar_ids_in_pool)]
    similar_rows = similar_rows.set_index('song_id').loc[
        [sid for sid in similar_ids_in_pool if sid in similar_rows['song_id'].values]
    ].reset_index()

    non_similar_rows = remaining_df[~remaining_df['song_id'].isin(similar_ids_in_pool)]
    non_similar_rows = non_similar_rows.sort_values('popularity', ascending=False)
    candidates = pd.concat([similar_rows, non_similar_rows], ignore_index=True)

    for i, (_, candidate) in enumerate(candidates.iterrows()):
        if i >= MAX_GUESSES:
            break
        print(f"Wait! Is it actually '{candidate['song_name']}' by {candidate['artists']}?")
        guess_text = f"'{candidate['song_name']}' by {candidate['artists']}"
        game_visualization.apply_guess_state(guess_text)

        print("(Yes / No) > ", end="", flush=True)
        PROMPT_READY.set()
        answer, source = ANSWER_QUEUE.get()
        if source == 'pygame':
            print(f"\033[92m{answer}\033[0m \n", end="", flush=True)
        answer = answer.strip().lower()
        if answer == "yes":
            game_visualization.initiate_final_result(True,
                                                     f"'{candidate['song_name']}' by {candidate['artists']}")
            harmonique_say("Aha! I knew I'd get there eventually.")
            harmonique_say("Restart the program to play another round!")
            return

    game_visualization.initiate_final_result(False, "You win this round. I am completely stumped!")
    harmonique_say("\nYou win this round. I am completely stumped!")
    reveal_and_check_database(full_df)


def reveal_and_check_database(df: pd.DataFrame) -> None:
    """Ask the user for their song and verify if it exists in the database.

    The 'Akinator' check: Prompts the console for title and artist, executing a
    case-insensitive lookup.

    Preconditions:
        - df is the full, unfiltered database DataFrame.
    """
    # 1. Update the top text and tell Pygame to show the input box
    game_visualization.current_question_state.question_text = "You win! What was the song?"
    game_visualization.ui_phase = "reveal"

    # 2. Ask for the Song
    game_visualization.input_prompt = "Enter Song Name:"
    u_song = get_text_input("Song Name")

    # 3. Ask for the Artist (Keep phase as 'reveal' so the box stays open)
    game_visualization.ui_phase = "reveal"
    game_visualization.input_prompt = "Enter Artist Name:"
    u_artist = get_text_input("Artist Name")

    # 4. Hide the input box by switching to the failure screen
    game_visualization.ui_phase = "failure"

    # Case-insensitive lookup in the dataset
    match = df[
        (df['song_name'].str.lower() == u_song.strip().lower())
        & (df['artists'].str.lower() == u_artist.strip().lower())
    ]

    # 5. Output the results to both the Console and the Pygame Window
    if not match.empty:
        actual = match.iloc[0]
        # Print to terminal
        print(f"\nWait, '{actual['song_name']}' is in my database!")
        print("My algorithms failed me... I should have caught that.")

        # Show on Pygame UI
        game_visualization.final_result_title = f"Wait, '{actual['song_name']}' is in my database!"
        game_visualization.final_result_subtitle = "My algorithms failed me... I should have caught that."
    else:
        # Print to terminal
        print(f"\nI don't have '{u_song}' by {u_artist} in my records.")
        print("No wonder I couldn't guess it! You've beaten me fairly.")

        # Show on Pygame UI
        game_visualization.final_result_title = f"I don't have '{u_song}' in my records."
        game_visualization.final_result_subtitle = "No wonder I couldn't guess it! You've beaten me fairly."


if __name__ == '__main__':
    main()
