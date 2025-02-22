from dataclasses import dataclass
from typing import Tuple

@dataclass
class InitData:
    exec_path: str
    data_path: str
    
@dataclass
class SolverData:
    considered_words: Tuple[str, ...]
    word_frequencies: dict[str, float]
    update_interval: float
    case_size: int

@dataclass
class InputData:
    available_algos: Tuple[str, ...]
    available_modes: Tuple[str, ...]
    data_size: int
    
@dataclass
class RuntimeData:
    shots: list[int]
    successes: int
    failures: int
    case: int
    algo: str