import json
from MineSweeper.core import MineSweeperService

mineSweeperService = MineSweeperService(3,3,3)
with open('prompt.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()
contents = []
gameDesStrList = []
dataNums = 50000
for i in range(dataNums):
    contents.append(prompt + mineSweeperService.GetCurGameDesString())
    gameDesStrList.append(mineSweeperService.GetCurGameDesString())
    mineSweeperService.RandomSafeClick()
    if mineSweeperService.IsGameOver():
        mineSweeperService.ReSetCurGame()
data_entries = [
    {"messages": [{"role": "user", "content": content}], "curgameDesStr": gameDesStr}
    for content, gameDesStr in zip(contents, gameDesStrList)
]
with open("MineSweeperData.jsonl", "w", encoding="utf-8") as f:

    for entry in data_entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
