from enum import Enum
import random

class Type(Enum):
    Empty = 0
    Number = 1
    Mine = 2

class Cell:
    def __init__(self, x, y):
        self.type = Type.Empty
        self.number = 0
        self.pos = (x, y)
        self.revealed = False
        self.exploded = False

class CellGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y) for y in range(height)] for x in range(width)]

    def IsAdjacent(self, cell1, cell2):
        x1, y1 = cell1.pos
        x2, y2 = cell2.pos
        return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1

    def GenerateMines(self, startCell, amount):
        for i in range(amount):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            while self.cells[x][y].type == Type.Mine or self.IsAdjacent(startCell, self.cells[x][y]):
                x += 1
                if x >= self.width:
                    x = 0
                    y += 1
                    if y >= self.height:
                        y = 0
            self.cells[x][y].type = Type.Mine
        return

    def GenerateNumbers(self):
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                if cell.type == Type.Mine:
                    continue
                cell.number = self.CountAdjacentMines(cell)
                cell.type = Type.Number if cell.number > 0 else Type.Empty
        return
            
    def CountAdjacentMines(self, cell):
        x, y = cell.pos
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                hasCell, adjacentCell = self.TryGetCell(x + i, y + j)
                if hasCell and adjacentCell.type == Type.Mine:
                    count += 1
        return count

    def TryGetCell(self, x, y):
        if self.InBounds(x, y):
            return True, self.cells[x][y]
        else:
            return False, None
    
    def InBounds(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

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
                        if cell.type == Type.Mine:
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
    
    def Click(self,x,y):
        if not self.generated:
            self.cellGrid.GenerateMines(self.cellGrid.cells[x][y],self.minesNum)
            self.cellGrid.GenerateNumbers()
            self.generated = True
        
        cell = self.cellGrid.cells[x][y]
        match cell.type:
            case Type.Mine:
                self.Explode(cell)
            case Type.Empty:
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
                if(cell.type == Type.Mine):
                    cell.revealed = True

    def Flood(self,floodBeginCell):
        if floodBeginCell.revealed:
            return
        if floodBeginCell.type == Type.Mine:
            return
        floodBeginCell.revealed = True
        if(floodBeginCell.type == Type.Number):
            return
        if(floodBeginCell.type == Type.Empty):
            x,y = floodBeginCell.pos
            for i in range(-1,2):
                for j in range(-1,2):
                    if i == 0 and j == 0:
                        continue
                    hasCell, adjacentCell = self.cellGrid.TryGetCell(x + i, y + j)
                    if hasCell and adjacentCell.type == Type.Empty:
                        self.Flood(adjacentCell)
                    if hasCell and adjacentCell.type == Type.Number:
                        adjacentCell.revealed = True
    
    def CheckWin(self):
        for i in range(self.width):
            for j in range(self.height):
                cell = self.cellGrid.cells[i][j]
                if cell.type != Type.Mine and not cell.revealed:
                    return
        self.gameOver = True
        self.gameWin = True
        self.gameLoss = False

class MineSweeperService:
    def __init__(self):
        self.curGame = None
    
    def GetCurGame(self):
        if self.curGame == None:
            self.curGame = MineSweeperGame()
        return self.curGame
    
    def ReSetCurGame(self):
        self.curGame = MineSweeperGame()
        return
