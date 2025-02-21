import os
import sys
class Solver:
    def __init__(self: "Solver") -> None:
        self.execution_path: str = os.path.dirname(sys.executable)
        
    def start(self: "Solver") -> None:
        print(self.execution_path)
