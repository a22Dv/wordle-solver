import os
import sys
from typing import Tuple, Type, Callable
from WordleSolver.initialize import WordData
from WordleSolver.data_structures import SolverData, InitData, InputData
from WordleSolver.algo import Context, Algorithm
from WordleSolver.input import Input


class Solver:
    def __init__(self: "Solver", context: Context) -> None:
        """Initialization."""
        self.init_data: InitData = InitData(
            os.path.dirname(sys.argv[0]),
            os.path.join(os.path.dirname(sys.argv[0]), "_internal", "data"),
        )
        self.solver_data = self._get_solver_data()
        self.context = context

    def _get_solver_data(self: "Solver") -> SolverData:
        """Helper method to get solver data."""
        considered_words: Tuple[str, ...] = WordData.get_words(self.init_data)
        solver_data: SolverData = SolverData(
            considered_words, WordData.get_freqs(considered_words), 0.0, 1
        )
        return solver_data

    def start(self: "Solver") -> None:
        """Main program loop."""
        algorithms: dict[str, Type["Algorithm"]] = self.context.get_algorithms()
        modes: tuple[str, str] = self.context.get_modes()
        input_data: InputData = InputData(
            tuple(algorithms.keys()),
            modes,
            len(self.solver_data.considered_words),
        )

        # Main loop.
        while True:
            input_algorithm: str = Input.get_algorithm(input_data)
            mode: str = Input.get_mode(input_data)
            if mode != "Real-time":
                self.solver_data.update_interval = Input.get_interval()
                self.solver_data.case_size = Input.get_case_size(input_data)
            else:
                self.solver_data.case_size = 1

            self.context.execute(input_algorithm, mode, self.solver_data)

            # Finish.
            print("Finished execution...")
            if input("Exit? (Y/n): ") in ("Y", "y"):
                sys.exit(0)
