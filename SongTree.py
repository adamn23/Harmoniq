"""
SongTree module for Harmoniq.
This module defines the SongTree class, a BST ADT
used to narrow down and identify a song the user is thinking of.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd

from Song import _Song
from Questions import QUESTIONS

ANSWER_OPTIONS = ['yes', 'no', 'i dont know']
YES, NO = ANSWER_OPTIONS[0], ANSWER_OPTIONS[1]


class SongTree:
    """
    Our Implementation of the BinarySearchTree ADT for the Harmonique Song Tree.

    Representation Invariants:
        - (_no_subtree is None) == (self._yes_subtree is None)
        - len(_songs) >= 1

    Instance Attributes:
        _question: The yes/no question stored at this node.
        _songs: The songs associated with this node.
        _no_subtree: The subtree for "no" answers, or None if this is a leaf.
        _yes_subtree: The subtree for "yes" answers, or None if this is a leaf.
    """
    songs: pd.Series[_Song]
    _question: tuple[str, str]
    _no_subtree: Optional[SongTree] = None
    _yes_subtree: Optional[SongTree] = None
    questions_asked: set[str]
    _split_scores: dict[tuple[str, str], int]

    def __init__(self, songs: pd.Series[_Song], questions_asked: set[str]):
        self.questions_asked = questions_asked
        self.songs = songs
        self._split_scores = {}
        self._question = ("", "")
        self._no_subtree = None
        self._yes_subtree = None

    def get_question(self) -> str:
        """
        Returns the private attribute self._question
        """
        return self._question[0].format(self._question[1])

    def is_leaf(self) -> bool:
        """
        Checks whether the current node is a leaf
        """
        return len(self.songs) <= 1 or len(self._split_scores) == 0

    def update_question(self) -> None:
        """
        Update self._question to refer to the next best question to ask
        (The question with the least error in self._split_scores).
        Remove this question from self._split_scores.
        Update the subtrees so that their song Series match the resulting Series of the new question.

        Preconditions:
            - self._split_scores != {}
        """
        if not self._split_scores:
            return
        self._question = min(self._split_scores, key=lambda x: self._split_scores[x])
        self._split_scores.pop(self._question)
        new_questions_asked = self.questions_asked | {self._question}
        self._yes_subtree = SongTree(self.songs, new_questions_asked.copy())
        self._no_subtree = SongTree(self.songs, new_questions_asked.copy())
        self.update_subtrees()

    def get_next_tree_state(self, answer: str) -> SongTree:
        """
        Create the next tree state based on the given answer

        Preconditions:
            - answer is not None
            - answer.lower() in ANSWER_OPTIONS
            - {} not in self._question
            - self._question is the question that the user just answered to

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
        """
        Update the dictionary of the next best questions not in questions_asked given the current set of songs.
        The next best question is defined as the question that splits up the set of songs closest to 50/50
        """
        for question in QUESTIONS:
            fill_value, split_error = self._create_split(question)
            filled = (question, fill_value)
            if filled not in self.questions_asked:
                self._split_scores[filled] = split_error

    def _create_split(self, general_question: str) -> tuple[str, int]:
        """
        Returns a tuple with element 0 as the *specific* question type to insert into the blanks ({}) of
        general_question and element 1 as the question's split error (difference in number of songs between
        answering yes and answering no)
        """
        attr = QUESTIONS[general_question]
        attr_series = self.songs.map(lambda s: getattr(s, attr))

        if _Song.__annotations__.get(attr) == bool:
            yes_count = int(attr_series.sum())
            no_count = len(self.songs) - yes_count
            return "", abs(yes_count - no_count)

        best_value, split_error = self._find_best_split_value(attr)
        return best_value, split_error

    def _find_best_split_value(self, attr) -> tuple[str, int]:
        """
        For categorical attributes (genre, emotion), tries each unique value
        as a yes/no split (is it X vs not X).

        For release_date, tries each unique year as a threshold (before X vs not).

        Args:
            attr: The attribute name to split on.

        Returns:
            A tuple of (best_value, best_error)
        """
        n = len(self.songs)
        best_value = None
        best_error = float('inf')

        if attr == "release_date":
            unique_years = set(getattr(s, attr)[:4] for s in self.songs)
            for year in unique_years:
                yes_count = sum(1 for s in self.songs if getattr(s, attr) < f'{year}-01-01')
                no_count = n - yes_count
                error = abs(yes_count - no_count)
                if error < best_error and yes_count and no_count:
                    best_error = error
                    best_value = year
        else:
            unique_values = set(getattr(s, attr) for s in self.songs)
            for value in unique_values:
                yes_count = sum(1 for s in self.songs if getattr(s, attr) == value)
                no_count = n - yes_count
                error = abs(yes_count - no_count)
                if error < best_error and yes_count and no_count:
                    best_error = error
                    best_value = value

        return best_value, int(best_error) if best_error != float('inf') else len(self.songs)

    def update_subtrees(self) -> None:
        """Update yes/no subtree songs based on the current question.

        Updates _yes_subtree.songs to songs that answer 'yes' to _question,
        and _no_subtree.songs to songs that answer 'no' to _question.
        """
        template, value = self._question
        attr = QUESTIONS[template]

        if _Song.__annotations__.get(attr) == bool:
            self._yes_subtree.songs = pd.Series([s for s in self.songs if getattr(s, attr)])
            self._no_subtree.songs = pd.Series([s for s in self.songs if not getattr(s, attr)])
        elif attr == "release_date":
            self._yes_subtree.songs = pd.Series([s for s in self.songs if s.release_date < value])
            self._no_subtree.songs = pd.Series([s for s in self.songs if s.release_date >= value])
        else:
            self._yes_subtree.songs = pd.Series([s for s in self.songs if getattr(s, attr) == value])
            self._no_subtree.songs = pd.Series([s for s in self.songs if getattr(s, attr) != value])
