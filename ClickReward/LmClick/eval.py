import os
import re
import requests
from MineSweeper.core import MineSweeperService

class EvalClass:
    def __init__(self,width = 3,height = 3,mineNum = 3):
        self.model = None
        self.mineGameService = MineSweeperService(width,height,mineNum)
        self.responsesInValidReward = -3
        self.clickIndexInValidReward = -2
        self.gameLossReward = -1
        self.safeClickReward = 1
        self.gameWinReward = 3
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            self.prompt = file.read()

    def LoadModel(self,modelName):
        fliePath = str(modelName) + ".sh"
        os.system(fliePath)

    def Sample(self,modelName,content):
        url = "http://localhost:8000/v1/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": modelName,
            "messages": [{"role": "user", "content": content}],
            "max_new_tokens": 2048,
            "length_penalty": 0.8,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.2,
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            generated_content = result['choices'][0]['message']['content']
            print("生成的内容:", generated_content)
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
        return generated_content

    def Reward(self, responses):
        responsesValid, clickX, clickY = self.ResponsesValid(responses)
        print(f"responsesValid:{responsesValid},clickX:{clickX},clickY:{clickY}")
        if not responsesValid:
            return self.responsesInValidReward
        curGame = self.mineGameService.GetCurGame()

        if not curGame.CanClick(clickX, clickY):
            return self.clickIndexInValidReward
        curGame.Click(clickX, clickY)

        if not curGame.gameOver:
            return self.safeClickReward
        elif curGame.gameLoss:
            self.mineGameService.ReSetCurGame()
            return self.gameLossReward
        elif curGame.gameWin:
            self.mineGameService.ReSetCurGame()
            return self.gameWinReward
        else:
            raise Exception("Game Over But Not Win Or Loss")

    def ResponsesValid(self, responses):
        # 使用正则表达式匹配 </think> 后面第一个形如 (a,b) 的结构
        pattern = r"</think>.*?\(\s*(\d)\s*,\s*(\d)\s*\)"
        match = re.search(pattern, responses, re.DOTALL)

        if match:
            a = int(match.group(1))
            b = int(match.group(2))
            print(f"a = {a}, b = {b}")
            return True, a, b
        else:
            print("没有在回答中找到正确的结构")
            return False, 0, 0

    def Eval(self, modelName, iter=10):
        print(f"modelName:{modelName}")
        totalReward = 0
        VaildIter = 0
        GameRun = 0
        WinRun = 0
        LossRun = 0
        for i in range(iter):
            print(f"{i+1}/{iter}")
            curGame = self.mineGameService.GetCurGame()
            gameDesString = curGame.GetGameDesString()
            print("curGame:\n"+gameDesString)
            content = self.prompt + gameDesString
            responses = self.Sample(modelName, content)
            reward = self.Reward(responses)
            match reward:
                case self.responsesInValidReward:
                    print("responsesInValid")
                case self.clickIndexInValidReward:
                    print("clickIndexInValid")
                case self.safeClickReward:
                    print("safeClick")
                    VaildIter += 1
                case self.gameWinReward:
                    print("GameWin")
                    VaildIter += 1
                    GameRun += 1
                    WinRun += 1
                case self.gameLossReward:
                    print("GameLoss")
                    VaildIter += 1
                    GameRun += 1
                    LossRun += 1
                case _:
                    print("Unexpected Reward")
            totalReward += reward
        print("Iter:", iter)
        print(f"VaildIter:{VaildIter}")
        print(f"GameRun:{GameRun}")
        print(f"WinRun:{WinRun}")
        print(f"LossRun:{LossRun}")
        print("Total Reward:", totalReward)
        print("Average Reward:", totalReward / iter)

if __name__ == "__main__":
    modelName = "DeepSeek-R1-Distill-Qwen-1.5B_grpo50"
    evalClass = EvalClass()
    evalClass.Eval(modelName,100)
    #gameDesString = evalClass.mineGameService.GetCurGame().GetGameDesString()
    #print(gameDesString)