# Harmoniq

An Akinator-style game that guesses the song you're thinking of from a dataset of about 900,000 Spotify tracks, by asking yes/no questions a person can actually answer.

## How it works

Harmoniq builds a decision tree on the fly. At each step it:

1. Looks at every candidate question ("Is this a love song?", "Was it released before 2010?", "Is the main artist a solo artist?").
2. Counts how many of the remaining songs would answer yes and how many would answer no.
3. Asks the question that splits the remaining songs most evenly, scored as `-p(1 - p)`, where `p` is the share answering yes. This is the Gini form of the split criterion, and it ranks questions the same way as information gain.
4. Keeps only the songs that match your answer. "I don't know" keeps the same songs and moves on to the next-best question.

A perfect 50/50 question halves the pool each time, so about 20 questions (log₂ 900,000 ≈ 19.8) are enough to narrow 900,000 songs down to one.

When the questions run out, Harmoniq guesses the most popular remaining song. If that guess is wrong, it falls back to a **song-similarity graph** built from Spotify's "similar songs" data and tries the closest neighbours of the wrong guess that are still possible, in order of similarity.

## Question types

| Type | Example | How it's scored |
|---|---|---|
| Yes/no feature | "Is the song about heartbreak?" | One split per feature |
| Category | "Is the genre hip hop?" | One split per value, only for values covering a meaningful share of the remaining songs |
| Threshold | "Was it released before 2010?" | Every year (or song length) scored in one pass with a cumulative sum |
| Artist | "Is it by [artist]?" | Only unlocked once 100 or fewer songs remain, so the game never lists artists one by one |

## Features engineered from the data

Every question had to be answerable by someone who knows the song well, so the dataset's raw audio scores are turned into plain-language features:

- **Lyric topic** (romance, heartbreak, hustle, partying, violence): topic keywords per 100 words; a topic is assigned only when it clearly dominates the runner-up.
- **Has a hook**: lyrics compressed with `zlib`. Repetitive lyrics compress well, so a low compression ratio means a lot of repetition.
- **Says the title in the lyrics**: fuzzy matching with RapidFuzz, so small spelling and punctuation differences don't break it.
- **Lyric style**: written in first person, addresses "you", contains a question, mentions a named place.
- **Mood**: happy, sad or angry, from positiveness and energy combined with the dataset's emotion label.
- **Metadata**: mainstream, fast-paced, high-energy, danceable, explicit, collaboration, primary genre, release year, length.
- **Artist details** from MusicBrainz: solo or group, gender, country.

## Performance

- Songs are stored as a **column-based pandas DataFrame**, so scoring a question is one vectorised comparison instead of a Python loop over 900,000 objects.
- The cleaned data is cached as **Parquet** and the similarity graph with **pickle**, so preprocessing runs only once and later games start almost instantly.

## Project structure

| File | Purpose |
|---|---|
| `main.py` | Loads or builds the caches, runs the game loop and the end-of-game guessing |
| `SongTree.py` | Question scoring, selection and splitting |
| `Questions.py` | The question templates and the column each one asks about |
| `SongGraph.py` | Weighted, undirected song-similarity graph |
| `Song.py` | The song object used as a graph vertex |
| `data_preprocessing.py` | Cleaning, feature engineering, MusicBrainz enrichment, graph building |
| `game_visualization.py` | Pygame interface |
| `input_bridge.py` | Background thread that reads console answers into a queue |
| `question_state.py` | State passed from the game to the interface |
| `CONSTANTS.py`, `PYGAME_CONSTANTS.py` | Thresholds, keyword lists and display settings |

## Getting started

1. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

2. Download the data and place it in the project folder:
   - Spotify dataset, saved as `spotify_dataset.csv`: [Kaggle](https://www.kaggle.com/datasets/devdope/900k-spotify) or [Google Drive](https://drive.google.com/file/d/1ToxzQl_8MvxG3nD2C26ZfmyQPVx93XFU/view?usp=sharing)
   - MusicBrainz artist data, `mb_artists.parquet`: [Google Drive](https://drive.google.com/file/d/1yqGUvsSxHpKIVPiUc1lCewHxZ779aTLv/view?usp=sharing)

3. Optional: skip the first-run preprocessing by downloading the prebuilt caches into the project folder:
   - [`song_tree_cache.parquet`](https://drive.google.com/file/d/14gyHud4tXnyeflfzF2_2KBPmTSAyrn__/view?usp=sharing)
   - [`song_graph_cache.pkl`](https://drive.google.com/file/d/18PGpqyEBAR-hTxuKVSnaoGczBBz1iQc6/view?usp=sharing)

   Only load cache files from a source you trust, since pickle files can run code when loaded.

4. Run the game:

   ```bash
   python main.py
   ```

   Think of a song, then answer each question with **yes**, **no** or **I don't know**, in the console or the game window.

## Limitations and next steps

- One wrong answer removes the right song permanently. Keeping a probability for every song and down-weighting mismatches, instead of deleting them, would let the game recover.
- Some questions are easier to answer reliably than others (genre more than release year). Weighting questions by how often players answer them correctly would make the game more robust.
- A simulation that plays thousands of games against random target songs would measure the average number of questions and the success rate.


## Data sources

- [900K Spotify dataset (Kaggle)](https://www.kaggle.com/datasets/devdope/900k-spotify)
- [MusicBrainz artist data](https://musicbrainz.org/doc/Artist)
