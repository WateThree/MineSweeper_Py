from .Cell import CellType
from .CellGrid import CellGrid

class MineSweeperGame:
    def __init__(self,width = 8,height = 8,minesNum = 10):
        self.width = width
        self.height = height
        self.minesNum = minesNum
        self.cellGrid = CellGrid(width,height)
        self.generated = False
        self.gameOver = False
        self.gameWin = False
        self.gameLoss = False

    def GetGameDesString(self):
        result = ""
        if not self.generated:
            for i in range(self.width):
                for j in range(self.height):
                    result += "B"
                result += "\n"
        else:
            for i in range(self.width):
                for j in range(self.height):
                    cell = self.cellGrid.cells[i][j]
                    if cell.revealed:
                        if cell.cellType == CellType.Mine:
                            result += "M"
                        else:
                            result += str(cell.number)
                    else:
                        result += "B"
                result += "\n"
        return result

    def CanClick(self,x,y):
        if not self.generated:
            return x >= 0 and x < self.width and y >= 0 and y < self.height
        else:
            return self.cellGrid.InBounds(x,y) and not self.cellGrid.cells[x][y].revealed
    
    def TryClick(self,x,y):
        if self.CanClick(x,y):
            self.Click(x,y)

    def Click(self,x,y):
        if not self.generated:
            self.cellGrid.GenerateMines(self.cellGrid.cells[x][y],self.minesNum)
            self.cellGrid.GenerateNumbers()
            self.generated = True
        
        cell = self.cellGrid.cells[x][y]
        match cell.cellType:
            case CellType.Mine:
                self.Explode(cell)
            case CellType.Empty:
                self.Flood(cell)
                self.CheckWin()
            case _:
                cell.revealed = True
                self.CheckWin()

    
    def Explode(self,explodeCell):
        self.gameOver = True
        self.gameLoss = True
        self.gameWin = False

        explodeCell.exploded = True
        explodeCell.revealed = True
        for i in range(self.width):
            for j in range(self.height):
                cell = self.cellGrid.cells[i][j]
                if(cell.cellType == CellType.Mine):
                    cell.revealed = True

    def Flood(self,floodBeginCell):
        if floodBeginCell.revealed:
            return
        if floodBeginCell.cellType == CellType.Mine:
            return
        floodBeginCell.revealed = True
        if(floodBeginCell.cellType == CellType.Number):
            return
        if(floodBeginCell.cellType == CellType.Empty):
            x,y = floodBeginCell.pos
            for i in range(-1,2):
                for j in range(-1,2):
                    if i == 0 and j == 0:
                        continue
                    hasCell, adjacentCell = self.cellGrid.TryGetCell(x + i, y + j)
                    if hasCell and adjacentCell.cellType == CellType.Empty:
                        self.Flood(adjacentCell)
                    if hasCell and adjacentCell.cellType == CellType.Number:
                        adjacentCell.revealed = True
    
    def CheckWin(self):
        for i in range(self.width):
            for j in range(self.height):
                cell = self.cellGrid.cells[i][j]
                if cell.cellType != CellType.Mine and not cell.revealed:
                    return
        self.gameOver = True
        self.gameWin = True
        self.gameLoss = False