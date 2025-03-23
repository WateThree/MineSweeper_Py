from enum import Enum

class Cell:
    def __init__(self, x, y):
        self.cellType = CellType.Empty
        self.number = 0
        self.pos = (x, y)
        self.revealed = False
        self.exploded = False

class CellType(Enum):
    Empty = 0
    Number = 1
    Mine = 2
