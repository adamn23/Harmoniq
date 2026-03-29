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

SongTree module for Harmoniq.
This module defines the SongTree class, a BST ADT
used to narrow down and identify a song the user is thinking of.

Optimized for large datasets (500k+ songs) by storing songs as a
DataFrame (one column per attribute) instead of a Series of _Song objects,
enabling vectorized pandas/numpy operations throughout.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
import numpy as np

from Questions import QUESTIONS, ARTIST_QUESTIONS

ANSWER_OPTIONS = ['yes', 'no', 'i dont know']
YES, NO = ANSWER_OPTIONS[0], ANSWER_OPTIONS[1]

# Artist questions are only injected once the pool shrinks to this size.
# Above this threshold, one-vs-rest artist splits are too narrow to be useful
# and would cause the game to enumerate artists one by one.
ARTIST_QUESTION_POOL_THRESHOLD = 50

# For categorical columns (album, primary_genre, artists), only generate a
# candidate question for a value if it covers at least this fraction of the
# current pool. Prevents useless questions like "Is it from album X?"
# when only 1 song in the pool is from that album.
MIN_CATEGORICAL_FRACTION = 0.02  # 2% of current pool, minimum 2 songs


def _gini_score(yes_count: int, no_count: int) -> float:
    """Return a Gini-based split quality score (lower = better split).

    Computes -(p_yes * p_no), which reaches its minimum of -0.25 at a
    perfect 50/50 split and rises toward 0 as the split becomes more
    imbalanced. Using a negative value keeps the convention that lower
    scores are better (consistent with minimizing split error).

    Args:
        yes_count: Number of songs in the yes branch.
        no_count: Number of songs in the no branch.

    Returns:
        A float in [-0.25, 0.0].
    """
    n = yes_count + no_count
    p_yes = yes_count / n
    p_no = no_count / n
    return -(p_yes * p_no)


class SongTree:
    """
    Our Implementation of the BinarySearchTree ADT for the Harmoniq Song Tree.
    Songs are stored as a DataFrame for vectorized performance.

    Representation Invariants:
        - (_no_subtree is None) == (self._yes_subtree is None)
        - len(df) >= 1

    Instance Attributes:
        df: DataFrame of songs, one row per song, one column per attribute.
        _question: The (template, fill_value) tuple for the current question.
        _no_subtree: The subtree for "no" answers, or None if this is a leaf.
        _yes_subtree: The subtree for "yes" answers, or None if this is a leaf.
        questions_asked: Set of (template, fill_value) tuples already used.
        _split_scores: Maps (template, fill_value) -> Gini score (lower is better).
    """

    df: pd.DataFrame
    _question: tuple[str, str]
    _no_subtree: Optional[SongTree]
    _yes_subtree: Optional[SongTree]
    questions_asked: set[tuple[str, str]]
    _split_scores: dict[tuple[str, str], float]

    def __init__(self, df: pd.DataFrame, questions_asked: set[tuple[str, str]]) -> None:
        """Initialize a SongTree node.

        Args:
            df: DataFrame of songs at this node, one row per song.
            questions_asked: Set of (template, fill_value) questions already used
                on the path from the root to this node.
        """
        self.df = df
        self.questions_asked = questions_asked
        self._split_scores = {}
        self._question = ("", "")
        self._no_subtree = None
        self._yes_subtree = None

    def get_question(self) -> str:
        """Return the current question as a formatted string.

        Returns:
            The current question with its fill value substituted in.
        """
        return self._question[0].format(self._question[1])

    def is_leaf(self) -> bool:
        """Check whether the current node is a leaf.

        A node is a leaf if it contains at most one song, or if there are
        no remaining questions to split on.

        Returns:
            True if this node is a leaf, False otherwise.
        """
        return len(self.df) <= 1 or len(self._split_scores) == 0

    def update_question(self) -> None:
        """Update self._question to the next best question (lowest Gini score).

        Selects the question with the minimum Gini score from self._split_scores,
        removes it from the scores dict, and creates the yes/no child subtrees
        by splitting self.df according to the chosen question.

        Preconditions:
            - self._split_scores != {}
        """
        if not self._split_scores:
            return

        self._question = min(self._split_scores, key=self._split_scores.__getitem__)
        self._split_scores.pop(self._question)
        self.questions_asked.add(self._question)

        new_asked = self.questions_asked | {self._question}
        yes_mask, no_mask = self._split_masks(self._question)

        self._yes_subtree = SongTree(
            self.df[yes_mask].reset_index(drop=True), new_asked.copy()
        )
        self._no_subtree = SongTree(
            self.df[no_mask].reset_index(drop=True), new_asked.copy()
        )

    def get_next_tree_state(self, answer: str) -> SongTree:
        """Return the next tree state based on the user's answer.

        For 'yes' or 'no', advances into the corresponding child subtree.
        For 'I don't know', stays at the current node and picks the next
        best question.

        Args:
            answer: The user's response. Must be one of ANSWER_OPTIONS.

        Returns:
            The next SongTree node to continue the game from.

        Preconditions:
            - answer is not None
            - answer.lower() in ANSWER_OPTIONS
            - self._question is the question the user just answered
        """
        answer = answer.lower()

        if answer == YES:
            self._yes_subtree.update_split_scores()
            self._yes_subtree.update_question()
            return self._yes_subtree
        elif answer == NO:
            self._no_subtree.update_split_scores()
            self._no_subtree.update_question()
            return self._no_subtree
        else:
            self.update_split_scores()
            self.update_question()
            return self

    def update_split_scores(self) -> None:
        """Score every candidate question and populate self._split_scores.

        For each question template in QUESTIONS (plus ARTIST_QUESTIONS once
        the pool is small enough), computes the Gini split score if the
        attribute column exists and the question has not already been asked.

        Routing logic per attribute type:
          - bool dtype or 0/1 values  → _score_bool_split
          - "release_date"            → _score_date_splits
          - "length"                  → _score_length_splits
          - everything else           → _score_categorical_splits
        """
        n = len(self.df)
        if n <= 1:
            return

        all_questions = dict(QUESTIONS)
        if n <= ARTIST_QUESTION_POOL_THRESHOLD:
            all_questions.update(ARTIST_QUESTIONS)

        for template, attr in all_questions.items():
            if attr not in self.df.columns:
                continue

            col = self.df[attr]

            if self._is_bool_col(col):
                self._score_bool_split(template, col, n)
            elif attr == "release_date":
                self._score_date_splits(template, col, n)
            elif attr == "length":
                self._score_length_splits(template, col, n)
            else:
                self._score_categorical_splits(template, col, n)

    # ── Scoring helpers ───────────────────────────────────────────────────────

    def _score_bool_split(self, template: str, col: pd.Series, n: int) -> None:
        """Score a boolean column as a single yes/no split and store the result.

        Args:
            template: The question template string (key in QUESTIONS).
            col: The boolean column from self.df.
            n: Total number of songs at this node.
        """
        key = (template, "")
        if key in self.questions_asked:
            return
        yes_count = int(col.sum())
        no_count = n - yes_count
        if yes_count and no_count:
            self._split_scores[key] = _gini_score(yes_count, no_count)

    def _score_categorical_splits(self, template: str, col: pd.Series, n: int) -> None:
        """Score each unique value of a categorical column as a yes/no split.

        Only considers values that cover at least MIN_CATEGORICAL_FRACTION of
        the current pool, preventing questions about rare one-off values.

        Args:
            template: The question template string (key in QUESTIONS).
            col: The categorical column from self.df.
            n: Total number of songs at this node.
        """
        min_count = max(2, int(n * MIN_CATEGORICAL_FRACTION))
        counts = col.value_counts()

        for value, yes_count in counts.items():
            if yes_count < min_count:
                continue
            no_count = n - yes_count
            if not (yes_count and no_count):
                continue
            key = (template, str(value))
            if key not in self.questions_asked:
                self._split_scores[key] = _gini_score(yes_count, no_count)

    def _score_date_splits(self, template: str, col: pd.Series, n: int) -> None:
        """Score each unique year as a threshold split (released before year X vs. not).

        Uses a cumulative sum over sorted year counts for an O(n log n) scan
        rather than an O(n * unique_years) loop.

        Args:
            template: The question template string (key in QUESTIONS).
            col: The release_date column from self.df (values like "YYYY-MM-DD").
            n: Total number of songs at this node.
        """
        years = col.str[:4].astype(int)
        counts = years.value_counts().sort_index()
        cumulative = counts.cumsum()
        sorted_years = np.sort(years.unique())

        for year in sorted_years:
            yes_count = int(cumulative.get(year - 1, 0))
            no_count = n - yes_count
            if not (yes_count and no_count):
                continue
            key = (template, str(year))
            if key not in self.questions_asked:
                self._split_scores[key] = _gini_score(yes_count, no_count)

    def _score_length_splits(self, template: str, col: pd.Series, n: int) -> None:
        """Score each unique whole-minute threshold as a yes/no split.

        Args:
            template: The question template string (key in QUESTIONS).
            col: The length column from self.df, in seconds.
            n: Total number of songs at this node.
        """
        minutes = (col // 60).astype(int)
        counts = minutes.value_counts().sort_index()
        cumulative = counts.cumsum()
        sorted_minutes = np.sort(minutes.unique())

        for minute in sorted_minutes:
            yes_count = int(cumulative.get(minute - 1, 0))
            no_count = n - yes_count
            if not (yes_count and no_count):
                continue
            key = (template, str(minute))
            if key not in self.questions_asked:
                self._split_scores[key] = _gini_score(yes_count, no_count)

    # ── Split mask ────────────────────────────────────────────────────────────

    def _split_masks(self, question: tuple[str, str]) -> tuple[pd.Series, pd.Series]:
        """Return (yes_mask, no_mask) boolean Series for the given question.

        Args:
            question: A (template, fill_value) tuple identifying the question.

        Returns:
            Two boolean Series of length len(self.df).
        """
        template, value = question
        all_questions = {**QUESTIONS, **ARTIST_QUESTIONS}
        attr = all_questions[template]
        col = self.df[attr]

        if self._is_bool_col(col):
            yes_mask = col.astype(bool)
            no_mask = ~yes_mask
        elif attr == "release_date":
            year_col = col.str[:4].astype(int)
            threshold = int(value)
            yes_mask = year_col < threshold
            no_mask = ~yes_mask
        elif attr == "length":
            threshold_seconds = int(value) * 60
            yes_mask = col > threshold_seconds
            no_mask = ~yes_mask
        else:
            # Categorical: exact match (primary_genre, album, artists)
            yes_mask = col == value
            no_mask = col != value

        return yes_mask, no_mask

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _is_bool_col(col: pd.Series) -> bool:
        """Check whether a column should be treated as boolean.

        Args:
            col: The column to inspect.

        Returns:
            True if the column has a bool dtype or contains only True/False/0/1
            values with at most 2 unique values.
        """
        return col.dtype == bool or (
            col.dropna().isin([True, False, 0, 1]).all()
            and col.nunique() <= 2
        )
