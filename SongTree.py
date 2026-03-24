from __future__ import annotations
from typing import Optional


class SongTree:
    """
    Our Implementation of the BinarySearchTree ADT for the Harmonique Song Tree.

    Representation Invariants:
        - (_no_subtree is None) == (self._yes_subtree is None)

    """

    _question: str
    _no_subtree: Optional[SongTree] = None
    _yes_subtree: Optional[SongTree] = None

    def __init__(self, question: str):
        self._question = question


    def get_question(self) -> str:
        return self._question

    def is_leaf(self) -> bool:
        return self._no_subtree is None
