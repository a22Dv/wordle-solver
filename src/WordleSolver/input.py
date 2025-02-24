from WordleSolver.data_structures import InputData
import os


class Input:
    @staticmethod
    def get_algorithm(data: InputData) -> str:
        while True:
            os.system("cls")
            for i, a in enumerate(data.available_algos):
                print(f"[{i + 1}] {a}")

            user_input: str = input("\nSelect algorithm no. (e.g. 0): ")
            if user_input.isnumeric() and 0 <= int(user_input) - 1 < len(
                data.available_algos
            ):
                return data.available_algos[int(user_input) - 1]

    @staticmethod
    def get_mode(data: InputData) -> str:
        while True:
            os.system("cls")
            for i, a in enumerate(data.available_modes):
                print(f"[{i + 1}] {a}")
            user_input: str = input("\nSelect mode. (e.g. 0): ")
            if user_input.isnumeric() and 0 <= int(user_input) - 1 < len(
                data.available_modes
            ):
                return data.available_modes[int(user_input) - 1]

    @staticmethod
    def get_interval() -> float:
        while True:
            os.system("cls")
            user_input: str = input(
                "Enter update interval in milliseconds (ms). (e.g. 5): "
            )
            if user_input.isdecimal():
                return float(user_input)

    @staticmethod
    def get_case_size(data: InputData) -> int:
        while True:
            os.system("cls")
            user_input: str = input("Enter test-case size (e.g. 500): ")
            if user_input.isnumeric() and int(user_input) < data.data_size:
                return int(user_input)

    @staticmethod
    def get_threshold() -> float:
        while True:
            os.system("cls")
            print(
                "A higher threshold limits the words considered.\n"
                "Solves faster & improve results, but set it too high, and it starts to\n" 
                "filter out possible answers. Chosen default is a balance between speed/thoroughness.\n"
            )
            user_input: str = input(
                "Enter frequency threshold (default: 5e-7 | 0.0000005): "
            )
            valid_decimal: bool = True
            try:
                float(user_input)
            except ValueError:
                valid_decimal = False
            if valid_decimal and 0.0 < float(user_input) < 0.5:
                return float(user_input)
            elif user_input == "":
                return 5e-7
