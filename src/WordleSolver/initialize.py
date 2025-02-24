import random
from typing import Tuple
from WordleSolver.data_structures import InitData
import wordfreq
import os


class WordData:
    @staticmethod
    def get_words(data: InitData) -> Tuple[str, ...]:
        """Gets the list of all 5-letter words in the dictionary."""
        WORD_LENGTH: int = 5
        TXT_PATH: str = os.path.join(data.data_path, "words.txt")
        if not os.path.exists(TXT_PATH):
            raise FileNotFoundError(f"Text file cannot be found at {TXT_PATH}")
        with open(TXT_PATH, "r") as FILE:
            return tuple([w for w in FILE.read().split("\n") if len(w) == WORD_LENGTH])

    @staticmethod
    def get_freqs(words: Tuple[str, ...]) -> dict[str, float]:
        """Returns a dictionary for a given set of words as keys to their frequency values."""
        return {word: wordfreq.word_frequency(word, "en") for word in words}
