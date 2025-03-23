from MineSweeper.core import MineSweeperService

def GameLoop(mineSweeperService:MineSweeperService,autoReset = True):
    print("input two number(0~n-1,split with space) to click somePlace.input R to reSetGame.input Q to Quit.")
    print("输入两个用空格分开的数字(0~n-1)来点击指定位置，输入R重置游戏，输入Q退出。")
    while True:
        gameDesString = mineSweeperService.GetCurGameDesString()
        print(gameDesString)
        data = input("Input:")
        inputData = data.split()
        if len(inputData) == 1:
            try:
                inputLetter = str(inputData[0])
                if inputLetter == 'r' or inputLetter == 'R':
                    mineSweeperService.ReSetCurGame()

                if inputLetter == 'q' or inputLetter == 'Q':
                    break
            except:
                print("formatError")
            
            if inputLetter == 'a':
                mineSweeperService.RandomClick()
        if len(inputData) == 2:
            try:
                clickX = int(inputData[0])
                clickY = int(inputData[1])
                mineSweeperService.TryClick(clickX,clickY)
            except:
                print("formatError")
        if autoReset:
            if mineSweeperService.IsGameOver():
                if mineSweeperService.IsGameWin():
                    print("You Win!")
                if mineSweeperService.IsGameLoss():
                    print(mineSweeperService.GetCurGameDesString())
                    print("You Loss!")
                mineSweeperService.ReSetCurGame()

mineSweeperService = MineSweeperService()
GameLoop(mineSweeperService)