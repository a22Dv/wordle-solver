import os
import re
import random
from abc import ABC, abstractmethod
from typing import Tuple, Type, Dict, Set, List
from WordleSolver.data_structures import SolverData, RuntimeData
from WordleSolver.display import Display, Console, MPL
from WordleSolver.utils import EntropyCalc, WordVector
from itertools import product
from time import sleep


class Context:  # TODO
    def get_algorithms(self: "Context") -> dict[str, Type["Algorithm"]]:
        return {
            "Random": Random,
            "Random Filtered": RandomFiltered,
            "Entropy": Entropy,
        }

    def get_modes(
        self: "Context",
    ) -> Tuple[str, str]:
        return ("Pre-defined", "Real-time")

    def get_evals(self: "Context") -> dict[str, Type["Evaluation"]]:
        return {
            "Pre-defined": Auto,
            "Real-time": User,
        }

    def execute(self: "Context", algorithm: str, mode: str, data: SolverData) -> None:
        """Entry point for execution."""

        available_algos: dict[str, Type[Algorithm]] = self.get_algorithms()
        available_evals: dict[str, Type[Evaluation]] = self.get_evals()

        ALGORITHM: Algorithm = available_algos[algorithm]()
        EVALUATION: Evaluation = available_evals[mode]()
        DISPLAY: Display = Console() if mode == "Real-time" else MPL()
        ALLOWED_GUESSES: int = 6

        # Stores shot-counts, success/failures, number of cases ran, nth_guess dist
        run_data: RuntimeData = RuntimeData([], 0, 0, 0, algorithm)

        # Answers for this run.
        case_data: list[str] = [
            random.choice(data.considered_words) for _ in range(data.case_size)
        ]

        for i in range(data.case_size):

            board: dict[str, Tuple[int, ...]] = {}
            attempts: int = 0
            is_success: bool = False
            for j in range(ALLOWED_GUESSES):

                # Predict.
                guesses: Tuple[Tuple[str, float], ...] = ALGORITHM.predict(data, board)

                # Set guess (Auto/User Input).
                # -2 = empty, -1 = absent, 0 = present, 1 = correct
                board[EVALUATION.guess(guesses, type(ALGORITHM) == Entropy)] = (
                    -2,
                    -2,
                    -2,
                    -2,
                    -2,
                )

                # Get feedback/evaluation of move. (Auto/User Eval)
                EVALUATION.evaluate(board, case_data[i])

                if type(DISPLAY) == Console:
                    DISPLAY.display(run_data, board, case_data[i])

                # Success.
                if (1, 1, 1, 1, 1) in set(board.values()):
                    attempts = j + 1
                    is_success = True
                    break

                # Failure.
                elif j == 5:
                    attempts = 7
                    is_success = False
                    break

            # Update data.
            run_data.shots.append(attempts)
            run_data.case += 1

            if is_success:
                run_data.successes += 1
            else:
                run_data.failures += 1

            DISPLAY.display(run_data, board, case_data[i])

            # Wait interval (Convert milliseconds to seconds).
            sleep(data.update_interval / 1000)


class Evaluation(ABC):
    @abstractmethod
    def guess(
        self: "Evaluation", guesses: Tuple[Tuple[str, float], ...], is_entropy: bool
    ) -> str:
        """Sets the final guess to the board."""
        pass

    @abstractmethod
    def evaluate(
        self: "Evaluation",
        board: dict[str, Tuple[int, ...]],
        answer: str,
    ) -> None:
        """Evaluates a guess based on feedback."""
        pass


class User(Evaluation):  # TODO
    def guess(
        self: "Evaluation", guesses: Tuple[Tuple[str, float], ...], is_entropy: bool
    ) -> str:
        while True:
            os.system("cls")
            for guess in guesses[0:20]:
                print(
                    f"{guess[0]} => {f"{f"{(guess[1] * 100):.3f}"}%" if not is_entropy else f"{guess[1]:.3f} B"}"
                )
            user_input: str = input("\nEnter your guess: ").lower()
            if not user_input.isalpha():
                continue
            elif user_input.lower() in [g[0] for g in guesses] or len(user_input) == 5:
                return user_input.lower()

    def evaluate(
        self: "Evaluation",
        board: dict[str, Tuple[int, ...]],
        answer: str,
    ) -> None:
        for entry in board.keys():
            os.system("cls")
            if board[entry] == (-2, -2, -2, -2, -2):
                evaluation: list[int] = [-2, -2, -2, -2, -2]
                while True:
                    os.system("cls")
                    print("Syntax: [Gray: -1, Yellow: 0, Green: 1]")
                    user_input: str = input("Enter feedback (e.g. -1 0 1 0 0): ")
                    pattern: str = r"(-1|0|1)(\s-1|\s0|\s1){4}"
                    if re.fullmatch(pattern, user_input):
                        evaluation = [int(n) for n in user_input.split()]
                        break
                board[entry] = tuple(evaluation)
                break


class Auto(Evaluation):  # TODO
    def guess(
        self: "Evaluation", guesses: Tuple[Tuple[str, float], ...], is_entropy: bool
    ) -> str:
        if not is_entropy:
            return random.choice(guesses)[0]
        else:
            return guesses[0][0]

    def evaluate(
        self: "Evaluation",
        board: dict[str, Tuple[int, ...]],
        answer: str,
    ) -> None:
        answer_count: WordVector = WordVector(answer)
        for entry in board.keys():
            if board[entry] == (-2, -2, -2, -2, -2):
                evaluation: list[int] = [-2, -2, -2, -2, -2]
                seen: Dict[str, int] = {}
                for i, chr in enumerate(entry):
                    if chr not in seen:
                        seen[chr] = 1
                    else:
                        seen[chr] += 1

                    within_count: bool = (
                        seen[chr]
                        <= answer_count.get_vector()[WordVector.map_to_num[chr]]
                    )
                    if within_count and chr == answer[i]:
                        evaluation[i] = 1
                    elif within_count and chr in answer and chr != answer[i]:
                        evaluation[i] = 0
                    else:
                        evaluation[i] = -1
                board[entry] = tuple(evaluation)


class Algorithm(ABC):
    @abstractmethod
    def predict(
        self: "Algorithm", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:
        """Returns a tuple of tuples of the predictions along with their prediction value
        for a given Wordle board until failure or success"""


class Random(Algorithm):
    def predict(
        self: "Random", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:
        # Does not use feedback as it is pure random.

        WORD_LIST: tuple[str, ...] = data.considered_words
        guesses: set = set()

        while len(guesses) < 20:
            guesses.add(random.choice(WORD_LIST))

        return tuple([(g, 1 / len(WORD_LIST)) for g in guesses])


class RandomFiltered(Algorithm):
    def predict(
        self: "RandomFiltered", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:
        WORD_LIST: tuple[str, ...] = data.considered_words
        summed_feedback: Dict[str, Dict[str, Set[int] | int]] = {
            k: {}
            for k in ("absent", "excluded", "min_counted", "max_counted", "correct")
        }
        col_guess: List[str] = [
            "".join([guess[i] for guess in board]) for i in range(5)
        ]
        col_fdbk: List[List[int]] = [
            [fdbk[i] for fdbk in board.values()] for i in range(5)
        ]
        for col, guess, fdbk in zip(range(5), col_guess, col_fdbk):
            for row, ltr, f_ltr in zip(range(6), guess, fdbk):
                if f_ltr == 1:
                    if ltr not in summed_feedback["correct"]:
                        summed_feedback["correct"][ltr] = set()
                    summed_feedback["correct"][ltr].add(col)
                elif f_ltr == 0:
                    if ltr not in summed_feedback["excluded"]:
                        summed_feedback["excluded"][ltr] = set()
                    summed_feedback["excluded"][ltr].add(col)
                elif (
                    f_ltr == -1
                    and ltr not in summed_feedback["correct"]
                    and ltr not in summed_feedback["excluded"]
                ):
                    if ltr not in summed_feedback["absent"]:
                        summed_feedback["absent"][ltr] = set()
                    summed_feedback["absent"][ltr].add(col)

        filtered_words: set = set()
        for word in WORD_LIST:
            is_v: bool = True
            for ltr in summed_feedback["absent"]:  # Gray check for absence.
                if ltr in word:
                    is_v = False
                    break
            if is_v:
                for ltr in summed_feedback["excluded"]:  # Yellow check for prescence.
                    if ltr not in word:
                        is_v = False
                        break
            if is_v:
                for ltr in summed_feedback[
                    "excluded"
                ]:  # Yellow check for position exclusion.
                    if any([word[i] == ltr for i in summed_feedback["excluded"][ltr]]):
                        is_v = False
                        break
            if is_v:
                for ltr in summed_feedback["correct"]:  # Green check for correctness.
                    if not all(
                        [word[i] == ltr for i in summed_feedback["correct"][ltr]]
                    ):
                        is_v = False
                        break
            if is_v:
                filtered_words.add(word)
        return tuple([(g, 1 / len(filtered_words)) for g in filtered_words])


class Entropy(Algorithm):
    def predict(
        self: "Entropy", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:
        auto_instance: Auto = Auto()
        rand_f_instance: RandomFiltered = RandomFiltered()

        VALID_GUESSES: Tuple[str, ...] = tuple(
            [g[0] for g in rand_f_instance.predict(data, board)]
        )
        guess_entropies: dict[str, float] = {}
        patterns: Tuple[Tuple[int, ...], ...] = tuple(
            [tuple(p) for p in product((-1, 0, 1), repeat=5)]
        )

        if 0 < len(board):
            for guess in VALID_GUESSES:
                entropy: float = EntropyCalc.get_entropy(
                    VALID_GUESSES, guess, patterns, auto_instance
                )
                guess_entropies[guess] = entropy

            return tuple([g for g in sorted(guess_entropies.items(), key=lambda t: t[1], reverse=True)[:10]])
        else:
            return tuple([(random.choice(("slate", "crane", "salet")), 1)])
