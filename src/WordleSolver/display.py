from abc import ABC, abstractmethod
from typing import Tuple
from WordleSolver.data_structures import RuntimeData
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import os


class Display(ABC):

    @abstractmethod
    def display(
        self: "Display",
        data: RuntimeData,
        board: dict[str, Tuple[int, ...]],
        answer: str,
    ) -> None:
        pass


class Console(Display):  # TODO
    """For Real-time data, only 1 attempt."""

    def display(
        self: "Display",
        data: RuntimeData,
        board: dict[str, Tuple[int, ...]],
        answer: str,
    ) -> None:
        os.system("cls")
        print(f"Active algorithm: {data.algo}")
        print("\nBoard state: \n")
        for guess in board:
            [print(f"{guess[i].upper()} ", end="") for i in range(5)]
            print()
        input("\nPress Enter to continue...")
        print("\n")


class MPL(Display):
    """For Pre-defined data, multiple attempts."""

    def __init__(self: "Display") -> None:
        plt.ion()
        plt.rcParams["font.family"] = "Cascadia Code"
        plt.style.use("dark_background")

    def display(
        self: "Display",
        data: RuntimeData,
        board: dict[str, Tuple[int, ...]],
        answer: str,
    ) -> None:

        # Data.
        success_rate: float = (data.successes / data.case) * 100
        bins: list[int] = list(range(1, 9))
        plt.cla()
        shot_count: Counter = Counter(data.shots)
        sorted_shots = sorted(shot_count.keys())
        freqs = [shot_count[shot] for shot in sorted_shots]
        max_freq: int = np.max(freqs)

        # Main plot.
        if data.shots:
            plt.plot(
                sorted_shots,
                freqs,
                color="white",
                linewidth=1,
                marker="o",
                linestyle="-",
            )
            for x, y in zip(sorted_shots, freqs):
                plt.plot(
                    [x, x],
                    [0, y],
                    color="white",
                    linestyle="--",
                    linewidth=1,
                    alpha=0.5,
                )
        plt.gca().set_xticks(bins[:-1])
        labels: list[str] = [f"{v}" for v in range(1, 7)]
        labels.append("UNSOLVED")
        plt.gca().set_xticklabels(labels)
        plt.title(f"Wordle n-Shots ({data.algo})")
        plt.xlabel("n-Shots")
        plt.ylabel("Frequency")

        x_align: float = 1.25
        plt.text(x_align, max_freq * 0.97, f"Case no.: {data.case}")
        plt.text(x_align, max_freq * 0.92, f"Success Rate: {success_rate:.2f}%")
        plt.text(
            x_align,
            max_freq * 0.87,
            f"Average n-shot: {f"{np.average(data.shots):.2f}" if np.average(data.shots) < 7 else "DID NOT SOLVE"}",
        )
        plt.text(x_align, max_freq * 0.82, f"Successful Attempts: {data.successes}")
        plt.text(x_align, max_freq * 0.77, f"Failed Attempts: {data.failures}")
        plt.show(block=False)
        plt.pause(0.02)

        # Console output.
        os.system("cls")
        print(f"Algorithm: {data.algo}")
        print(
            f"Average n-shot: {f"{np.average(data.shots):.2f}" if np.average(data.shots) < 7 else "FAILED"}"
        )
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Successful Attempts: {data.successes}")
        print(f"Failed Attempts: {data.failures}")
        print(f"Case no.: {data.case}")
        print(f"\nAnswer: {answer}\n")
        for guess, val in board.items():
            print(f"{guess} | {val}")
