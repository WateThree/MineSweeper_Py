from .MineSweeperGame import MineSweeperGame

class MineSweeperService:
    def __init__(self,height = 8,width = 8,mineNum = 10):
        self.curGame = None
        self.width = width
        self.height = height
        self.mineNum = mineNum
    
    def GetCurGame(self):
        if self.curGame is None:
            self.curGame = MineSweeperGame(self.width,self.height,self.mineNum)
        return self.curGame
    
    def ReSetCurGame(self):
        self.curGame = MineSweeperGame(self.width,self.height,self.mineNum)
        return
    
    def GetCurGameDesString(self):
        curGame : MineSweeperGame = self.GetCurGame()
        curGameDesString : str = curGame.GetGameDesString()
        return curGameDesString
    
    def TryClick(self,ClickX,ClickY):
        curGame = self.GetCurGame()
        curGame.TryClick(ClickX,ClickY)
    
    def IsGameOver(self):
        return self.GetCurGame().gameOver
    
    def IsGameWin(self):
        return self.GetCurGame().gameWin
    
    def IsGameLoss(self):
        return self.GetCurGame().gameLoss
    
    def IsGameStart(self):
        return not self.GetCurGame().generated
    
    def RandomClick(self):
        self.GetCurGame().RandomClick()

    def RandomSafeClick(self):
        self.GetCurGame().RandomSafeClick()
        
