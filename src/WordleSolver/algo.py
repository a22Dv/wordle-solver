from abc import ABC, abstractmethod
from typing import Tuple, Type
from WordleSolver.data_structures import SolverData, RuntimeData
import random
import os
import re
from WordleSolver.display import Display, Console, MPL
from WordleSolver.utils import WordVector
from time import sleep


class Context:  # TODO
    def get_algorithms(self: "Context") -> dict[str, Type["Algorithm"]]:
        return {
            "Random": Random,
            "Random Filtered": RandomFiltered,
            "Letter Frequency": LetterFrequency,
            "Word Frequency": WordFrequency,
            "Entropy": Entropy,
            "Hybrid": Hybrid,
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
                board[EVALUATION.guess(guesses)] = (-2, -2, -2, -2, -2)

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
        self: "Evaluation",
        guesses: Tuple[Tuple[str, float], ...],
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
        self: "Evaluation",
        guesses: Tuple[Tuple[str, float], ...],
    ) -> str:
        while True:
            os.system("cls")
            for guess in guesses[0:20]:
                print(f"{guess[0]} => {(guess[1] * 100):.3f}%")

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
        self: "Evaluation",
        guesses: Tuple[Tuple[str, float], ...],
    ) -> str:
        return random.choice(guesses)[0]

    # TODO: Implement position-awareness
    def evaluate(
        self: "Evaluation",
        board: dict[str, Tuple[int, ...]],
        answer: str,
    ) -> None:
        for entry in board.keys():
            if board[entry] == (-2, -2, -2, -2, -2):
                evaluation: list[int] = [-2, -2, -2, -2, -2]
                answer_count: Tuple[int, ...] = WordVector(answer).get_vector()
                seen: dict[str, int] = {}
                for i, ch in enumerate(entry):
                    if ch not in seen:
                        seen[ch] = 1
                    else:
                        seen[ch] += 1
                    if (
                        ch not in answer
                        or answer_count[WordVector.map_to_num[ch]] < seen[ch]
                    ):
                        evaluation[i] = -1
                    elif ch in answer and answer[i] != ch:
                        evaluation[i] = 0
                    else:
                        evaluation[i] = 1
                board[entry] = tuple(evaluation)
                break


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
        # Does not use board as it is pure random.

        WORD_LIST: tuple[str, ...] = data.considered_words
        guesses: set = set()

        while len(guesses) < 20:
            guesses.add(random.choice(WORD_LIST))

        return tuple([(g, 1 / len(WORD_LIST)) for g in guesses])


class RandomFiltered(Algorithm):
    def predict(
        self: "RandomFiltered", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:

         # Broken.
        pass
class LetterFrequency(Algorithm):  # TODO
    def predict(
        self: "LetterFrequency", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:

        pass


class WordFrequency(Algorithm):  # TODO
    def predict(
        self: "WordFrequency", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:

        pass


class Entropy(Algorithm):  # TODO
    def predict(
        self: "Entropy", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:

        pass


class Hybrid(Algorithm):  # TODO
    def predict(
        self: "Hybrid", data: SolverData, board: dict[str, Tuple[int, ...]]
    ) -> Tuple[Tuple[str, float], ...]:

        pass
