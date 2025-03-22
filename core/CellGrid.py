from .Cell import Cell,CellType
import random

class CellGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y) for y in range(height)] for x in range(width)]

    def IsSameCell(self,cell : Cell,compareCell : Cell):
        return cell.pos == compareCell.pos

    def GenerateMines(self, startCell, amount):
        for _ in range(amount):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            while self.cells[x][y].cellType == CellType.Mine or self.IsSameCell(startCell,self.cells[x][y]):
                x += 1
                if x >= self.width:
                    x = 0
                    y += 1
                    if y >= self.height:
                        y = 0
            self.cells[x][y].cellType = CellType.Mine
        return

    def GenerateNumbers(self):
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                if cell.cellType == CellType.Mine:
                    continue
                cell.number = self.CountAdjacentMines(cell)
                cell.cellType = CellType.Number if cell.number > 0 else CellType.Empty
        return
            
    def CountAdjacentMines(self, cell):
        x, y = cell.pos
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                hasCell, adjacentCell = self.TryGetCell(x + i, y + j)
                if hasCell and adjacentCell.cellType == CellType.Mine:
                    count += 1
        return count

    def TryGetCell(self, x, y):
        if self.InBounds(x, y):
            return True, self.cells[x][y]
        else:
            return False, None
    
    def InBounds(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height
