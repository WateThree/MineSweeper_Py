import asyncio
import re
from typing import List

import json
from transformers import AutoTokenizer

from swift.plugin import ORM, orms
from swift.utils import get_logger
from MineSweeper.core import MineSweeperService,MineSweeperGame,Cell,CellType
import hashlib
import json


logger = get_logger()


# Code borrowed from plugin/orm.py
class RewardSingleData:
    def __init__(self, curGame : MineSweeperGame, clickX, clickY,reward = 0):
        self.curGame = curGame
        self.clickX = clickX
        self.clickY = clickY
        self.reward = reward
    
    def GetHashValue(self):
        return calculate_string_hash(self.curGame.GetGameDesString()+str(self.clickX)+str(self.clickY))

class RewardValueClass:
    def __init__(self,curRewardValue):
        self.curRewardValue = curRewardValue
        self.Count = 1

    def CalculateAverage(self,newRewardValue):
        self.curRewardValue = float(self.curRewardValue*self.Count + newRewardValue)/float(self.Count+1)
        self.Count += 1

class RewardData:
    def __init__(self,desStr="Default"):
        self.rewardDataDict = {}
    
    def AddRewardSingleData(self,rewardSingleData):
        curGameHashValue = rewardSingleData.GetHashValue()
        if self.rewardDataDict.get(curGameHashValue,None) is None:
            self.rewardDataDict.setdefault(curGameHashValue,RewardValueClass(rewardSingleData.reward))
        else:
            self.rewardDataDict[curGameHashValue].CalculateAverage(float(rewardSingleData.reward))
        
    def GetRewardValueDataCurRewardValue(self,rewardSingleData:RewardSingleData):
        curGameHashValue = rewardSingleData.GetHashValue()
        rewardValueClass : RewardValueClass = self.rewardDataDict.get(curGameHashValue,None)
        if  rewardValueClass is None:
            return False,None
        else:
            return True,rewardValueClass.curRewardValue

    def ClearRewardData(self):
        self.rewardDataDict.clear()

def calculate_string_hash(s):
    hash_obj = hashlib.new("sha256")
    hash_obj.update(s.encode("utf-8"))
    return hash_obj.hexdigest()

def CalculateRewardData(mineSweeperService:MineSweeperService,iter=1000000):
    mineSweeperService = MineSweeperService(height=3,width = 3,mineNum = 3)
    rewardData = RewardData()
    for _ in range(iter):
        if mineSweeperService.IsGameOver():
            mineSweeperService.ReSetCurGame()
        mineSweeperService.RandomSafeClick()
        curGame = mineSweeperService.GetCurGame()
        for unRevealedCellIndex in curGame.UnRevealedSet:
            unRevealedCell = curGame.cellGrid.cells[unRevealedCellIndex[0]][unRevealedCellIndex[1]]
            unRevealedCell : Cell
            if unRevealedCell.cellType == CellType.Mine:
                reward = -2
            else:
                reward = 1
            rewardSingleData = RewardSingleData(curGame=curGame,
                                                clickX= unRevealedCell.pos[0],
                                                clickY=unRevealedCell.pos[1],
                                                reward=reward)
            rewardData.AddRewardSingleData(rewardSingleData=rewardSingleData)
    return rewardData

class MineSweeperReward(ORM): 
    def __init__(self):
        self.rewardData = RewardData()
        mineSweeperService = MineSweeperService(3,3,3)
        self.rewardData = CalculateRewardData(mineSweeperService=mineSweeperService,iter=1000000)
        self.responsesInValidReward = -1.0
        self.clickIndexInValidReward = -1.0

    def GetRewardValue(self,gameDesAndClickString:str):
        curGameHashValue = calculate_string_hash(gameDesAndClickString)
        rewardValueClass : RewardValueClass = self.rewardData.rewardDataDict.get(curGameHashValue,None)
        if  rewardValueClass is None:
            return False,None
        else:
            return True,rewardValueClass.curRewardValue

    def ResponsesValid(self, responses):
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

    def __call__(self,completions,curgameDesStr,**kwargs):
        rewardList = []
        for completion,sampleGameDesStr in zip(completions,curgameDesStr):
            responsesValid, clickX, clickY = self.ResponsesValid(str(completion))
            print(f"responsesValid:{responsesValid},clickX:{clickX},clickY:{clickY}")
            if not responsesValid:
                rewardList.append(self.responsesInValidReward)
                continue
            if str(sampleGameDesStr) == "BBB\nBBB\nBBB\n":
                if clickX >=0 and clickX<=2 and clickY >=0 and clickY <=2:
                    rewardList.append(1.0)
                    continue
                else:
                    print(f"clickXclickY无效或越界，clickX：{clickX},clickY:{clickY}")
                    rewardList.append(self.clickIndexInValidReward)
                    continue
            gameDesAndClickString=str(sampleGameDesStr)+str(clickX)+str(clickY)
            rewardVaild,rewardValue = self.GetRewardValue(gameDesAndClickString)
            if not rewardVaild:
                print(f"clickXclickY无效或越界，clickX：{clickX},clickY:{clickY}")
                rewardList.append(self.clickIndexInValidReward)
                continue
            else:
                print(f"找到了对应的字典键,rewardValue:{rewardValue}")
                rewardList.append(rewardValue)
                continue
        
        return rewardList

class LengthReward(ORM): 
    def __call__(self,completions, **kwargs):
        rewardList = []
        for completion in completions:
            responsesValid, clickX, clickY = self.ResponsesValid(str(completion))
            print(f"responsesValid:{responsesValid},clickX:{clickX},clickY:{clickY}")
            if not responsesValid:
                rewardList.append(-1.0)
                continue
            tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
            responseLen = len(tokenizer.encode(completion))
            if responseLen < 1024:
                rewardList.append(1.0)
                continue
            else:
                print(f"Len:{responseLen}")
                print(f"LenReward:{1.0 - ((responseLen-1024.0)/1024.0)}")
                rewardList.append(1.0 - ((responseLen-1024.0)/1024.0))
                continue
        
        return rewardList
    
    def ResponsesValid(self, responses):
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


    
class MathAccuracy(ORM):

    def __init__(self):
        import importlib.util
        assert importlib.util.find_spec('math_verify') is not None, (
            "The math_verify package is required but not installed. Please install it using 'pip install math_verify'.")

    def __call__(self, completions, solution, **kwargs) -> List[float]:
        from latex2sympy2_extended import NormalizationConfig
        from math_verify import LatexExtractionConfig, parse, verify
        rewards = []
        for content, sol in zip(completions, solution):
            gold_parsed = parse(sol, extraction_mode='first_match', extraction_config=[LatexExtractionConfig()])
            if len(gold_parsed) != 0:
                # We require the answer to be provided in correct latex (no malformed operators)
                answer_parsed = parse(
                    content,
                    extraction_config=[
                        LatexExtractionConfig(
                            normalization_config=NormalizationConfig(
                                nits=False,
                                malformed_operators=False,
                                basic_latex=True,
                                equations=True,
                                boxed=True,
                                units=True,
                            ),
                            # Ensures that boxed is tried first
                            boxed_match_priority=0,
                            try_extract_without_anchor=False,
                        )
                    ],
                    extraction_mode='first_match',
                )
                # Reward 1 if the content is the same as the ground truth, 0 otherwise
                reward = float(verify(answer_parsed, gold_parsed))
            else:
                # If the gold solution is not parseable, we reward 1 to skip this example
                reward = 1.0
            rewards.append(reward)
        return rewards


class MathFormat(ORM):

    def __call__(self, completions, **kwargs) -> List[float]:
        """Reward function that checks if the completion has a specific format."""
        pattern = r'^<think>.*?</think>\s*<answer>.*?</answer>(?![\s\S])'
        matches = [re.match(pattern, content, re.DOTALL | re.MULTILINE) for content in completions]
        return [1.0 if match else 0.0 for match in matches]


class CountdownORM(ORM):

    def __call__(self, completions, target, nums, **kwargs) -> List[float]:
        """
        Evaluates completions based on Mathematical correctness of the answer

        Args:
            completions (list[str]): Generated outputs
            target (list[str]): Expected answers
            nums (list[str]): Available numbers

        Returns:
            list[float]: Reward scores
        """
        rewards = []
        for completion, gt, numbers in zip(completions, target, nums):
            try:
                # Check if the format is correct
                match = re.search(r'<answer>(.*?)<\/answer>', completion)
                if match is None:
                    rewards.append(0.0)
                    continue
                # Extract the "answer" part from the completion
                equation = match.group(1).strip()
                if '=' in equation:
                    equation = equation.split('=')[0]
                # Extract all numbers from the equation
                used_numbers = [int(n) for n in re.findall(r'\d+', equation)]

                # Check if all numbers are used exactly once
                if sorted(used_numbers) != sorted(numbers):
                    rewards.append(0.0)
                    continue
                # Define a regex pattern that only allows numbers, operators, parentheses, and whitespace
                allowed_pattern = r'^[\d+\-*/().\s]+$'
                if not re.match(allowed_pattern, equation):
                    rewards.append(0.0)
                    continue

                # Evaluate the equation with restricted globals and locals
                result = eval(equation, {"__builti'ns__": None}, {})
                # Check if the equation is correct and matches the ground truth
                if abs(float(result) - float(gt)) < 1e-5:
                    rewards.append(1.0)
                else:
                    rewards.append(0.0)
            except Exception:
                # If evaluation fails, reward is 0
                rewards.append(0.0)
        return rewards


class MultiModalAccuracyORM(ORM):

    def __call__(self, completions, solution, **kwargs) -> List[float]:
        """
        Reward function that checks if the completion is correct.
        Args:
            completions (list[str]): Generated outputs
            solution (list[str]): Ground Truths.

        Returns:
            list[float]: Reward scores
        """
        rewards = []
        from math_verify import parse, verify
        for content, sol in zip(completions, solution):
            reward = 0.0
            # Try symbolic verification first
            try:
                answer = parse(content)
                if float(verify(answer, parse(sol))) > 0:
                    reward = 1.0
            except Exception:
                pass  # Continue to next verification method if this fails

            # If symbolic verification failed, try string matching
            if reward == 0.0:
                try:
                    # Extract answer from solution if it has think/answer tags
                    sol_match = re.search(r'<answer>(.*?)</answer>', sol)
                    ground_truth = sol_match.group(1).strip() if sol_match else sol.strip()

                    # Extract answer from content if it has think/answer tags
                    content_match = re.search(r'<answer>(.*?)</answer>', content)
                    student_answer = content_match.group(1).strip() if content_match else content.strip()

                    # Compare the extracted answers
                    if student_answer == ground_truth:
                        reward = 1.0
                except Exception:
                    pass  # Keep reward as 0.0 if both methods fail
            rewards.append(reward)
        return rewards


# ref implementation: https://github.com/huggingface/open-r1/blob/main/src/open_r1/rewards.py
class CodeReward(ORM):

    def __init__(self):
        import importlib.util
        assert importlib.util.find_spec('e2b') is not None, (
            "The e2b package is required but not installed. Please install it using 'pip install e2b-code-interpreter'."
        )
        from dotenv import load_dotenv
        load_dotenv()

    @staticmethod
    def extract_code(completion: str, language: str) -> str:
        pattern = re.compile(rf'```{language}\n(.*?)```', re.DOTALL)
        matches = pattern.findall(completion)
        extracted_answer = matches[-1] if len(matches) >= 1 else ''
        return extracted_answer

    def run_async_from_sync(self, scripts: List[str], languages: List[str]) -> List[float]:
        """Function wrapping the `run_async` function."""
        # Create a new event loop and set it
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the async function and get the result
            rewards = loop.run_until_complete(self.run_async(scripts, languages))
        finally:
            loop.close()

        return rewards

    async def run_async(self, scripts: List[str], languages: List[str]) -> List[float]:
        from e2b_code_interpreter import AsyncSandbox

        # Create the sandbox by hand, currently there's no context manager for this version
        try:
            sbx = await AsyncSandbox.create(timeout=30, request_timeout=3)
        except Exception as e:
            logger.warning(f'Error from E2B executor: {e}')
            return [0.0] * len(scripts)
        # Create a list of tasks for running scripts concurrently
        tasks = [self.run_script(sbx, script, language) for script, language in zip(scripts, languages)]

        # Wait for all tasks to complete and gather their results as they finish
        results = await asyncio.gather(*tasks)
        rewards = list(results)  # collect results

        # Kill the sandbox after all the tasks are complete
        await sbx.kill()

        return rewards

    async def run_script(self, sbx, script: str, language: str) -> float:
        try:
            execution = await sbx.run_code(script, language=language, timeout=30)
        except Exception as e:
            logger.warning(f'Error from E2B executor: {e}')
            return 0.0
        try:
            return float(execution.text)
        except (TypeError, ValueError):
            return 0.0

    def __call__(self, completions, **kwargs) -> List[float]:
        """Reward function that evaluates code snippets using the E2B code interpreter.

        Assumes the dataset contains a `verification_info` column with test cases.
        """
        evaluation_script_template = """
        import subprocess
        import json

        def evaluate_code(code, test_cases):
            passed = 0
            total = len(test_cases)
            exec_timeout = 5

            for case in test_cases:
                process = subprocess.run(
                    ["python3", "-c", code],
                    input=case["input"],
                    text=True,
                    capture_output=True,
                    timeout=exec_timeout
                )

                if process.returncode != 0:  # Error in execution
                    continue

                output = process.stdout.strip()
                if output.strip() == case["output"].strip():
                    passed += 1

            success_rate = (passed / total)
            return success_rate

        code_snippet = {code}
        test_cases = json.loads({test_cases})

        evaluate_code(code_snippet, test_cases)
        """
        verification_info = kwargs['verification_info']
        languages = [info['language'] for info in verification_info]
        code_snippets = [
            self.extract_code(completion, language) for completion, language in zip(completions, languages)
        ]
        scripts = [
            evaluation_script_template.format(
                code=json.dumps(code), test_cases=json.dumps(json.dumps(info['test_cases'])))
            for code, info in zip(code_snippets, verification_info)
        ]
        try:
            rewards = self.run_async_from_sync(scripts, languages)

        except Exception as e:
            logger.warning(f'Error from E2B executor: {e}')
            rewards = [0.0] * len(completions)

        return rewards


class CodeFormat(ORM):

    def __call__(self, completions, **kwargs) -> List[float]:
        verification_info = kwargs['verification_info']
        rewards = []
        for content, info in zip(completions, verification_info):
            pattern = r'^<think>.*?</think>\s*<answer>.*?```{}.*?```.*?</answer>(?![\s\S])'.format(info['language'])
            match = re.match(pattern, content, re.DOTALL | re.MULTILINE)
            reward = 1.0 if match else 0.0
            rewards.append(reward)
        return rewards


    
orms['LengthReward'] = LengthReward
orms['MineSweeperReward'] = MineSweeperReward
orms['external_math_acc'] = MathAccuracy
orms['external_math_format'] = MathFormat
orms['external_countdown'] = CountdownORM
orms['external_r1v_acc'] = MultiModalAccuracyORM
orms['external_code_reward'] = CodeReward
orms['external_code_format'] = CodeFormat
