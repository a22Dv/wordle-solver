from typing import Tuple, TYPE_CHECKING
from math import log2

if TYPE_CHECKING:
    from WordleSolver.algo import Auto


class WordVector:
    map_to_num = {k: v for k, v in zip("abcdefghijklmnopqrstuvwxyz", range(26))}

    def __init__(self: "WordVector", string: str) -> None:
        self._vector: list[int] = [0 for _ in range(26)]
        for c in string:
            self._vector[self.map_to_num[c]] += 1

    def get_vector(self: "WordVector") -> Tuple[int, ...]:
        return tuple(self._vector)

    @staticmethod
    def in_sup_vector(sub_vector: "WordVector", sup_vector: "WordVector") -> bool:
        """Checks if sub-vector is within sup-vector. Each element in sub_vector must be <= the corresponding
        element in the sup-vector."""
        for x, y in zip(sub_vector.get_vector(), sup_vector.get_vector()):
            if x > y:
                return False
        return True


class EntropyCalc:
    @staticmethod
    def get_entropy(
        word_list: Tuple[str, ...], guess: str, patterns: Tuple[Tuple[int, ...], ...], eval: "Auto"
    ) -> float:
        p_count: dict[Tuple[int, ...], int] = {k: 0 for k in patterns}
        for word in word_list:
            word_pattern: dict[str, Tuple[int, ...]] = {word: (-2, -2, -2, -2, -2)}
            eval.evaluate(word_pattern, guess)
            p_count[word_pattern[word]] += 1
        entropy: float = 0.0
        word_list_len: int = len(word_list)
        for p in p_count:
            prob: float = p_count[p] / word_list_len
            entropy += prob * (log2(prob) if prob else 0)
        return -entropy if entropy != 0 else 0
