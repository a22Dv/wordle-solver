from typing import Tuple


class WordVector:
    map_to_num = {k: v for k, v in zip("abcdefghijklmnopqrstuvwxyz", range(26))}

    def __init__(self: "WordVector", string: str) -> None:
        self._vector: list[int] = [0 for _ in range(26)]
        for c in string:
            self._vector[self.map_to_num[c]] += 1


    def get_vector(self: "WordVector") -> Tuple[int, ...]:
        return tuple(self._vector)

    @classmethod
    def in_sup_vector(sub_vector: "WordVector", sup_vector: "WordVector") -> bool:
        """Checks if sub-vector is within sup-vector. Each element in sub_vector must be <= the corresponding
        element in the sup-vector."""
        for x, y in zip(sub_vector.get_vector(), sup_vector.get_vector()):
            if x > y:
                return False
        return True
