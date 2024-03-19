import openai
from scripts.question import Question

from typing import List, Dict, Any

import json

class KahootQuestionGenerator:
    def __init__ (self) -> None:
        #Load credentials
        self._questions: List[Question] = []
        self._title = ''
        secrets_dict: Dict[str,str] = None
        self.api_key: str = None

        with open("secrets.json", "r") as secrets:
            secrets_dict = json.load(secrets)
            self.api_key = secrets_dict["OpenAI"]["APIKey"]
        openai.api_key = self.api_key

    def request_questions(self, number: str, theme: str) -> bool:
        promt_text: str = """
            give me a list of [N] facts related to [THEME] that would result in good kahoot questions.
            output styple: {"facts":[fact1, fact2...],

            For each of those, create a Kahoot quiz on the theme [THEME] with [N] questions. Mix both Multiple Choice and True-False questions. For each question, provide a clear and concise stem, along with answer options or a True-False statement, and a image description. 
            Output style:
            "title": "questions": [{"question":,"image_description":,"choices":,"correct_index":,"time":}]}

            Unite both on one json file.

        """ + f'Theme: {theme}, N: {number}'

        quiz_in_json:str = openai.chat.completions.create(
            model='gpt-3.5-turbo-0125',
            messages= [{
                'role': 'user',
                'content': promt_text
                }]
        ).choices[0].message.content
        self.quiz_in_json = quiz_in_json
        self.json_to_dict(quiz_in_json)
    
    def json_to_dict(self, json_quis: str):
        quiz: Dict[str, Dict[str,str]] = json.loads(json_quis)

        for i, info in enumerate(quiz):
            if i:
                key = info
        quiz = quiz[key][0]
        dict_questions = quiz['questions']
        self._title = quiz['title']
        self._dict_to_questions(dict_questions)

    def _dict_to_questions(self, dict_questions: Dict[str,Any]):
        self._questions = []
        for question in dict_questions:
            time_limit = 0
            if question['time'] >= 45:
                time_limit = 4
            elif question['time'] >= 25:
                time_limit = 3
            elif question['time'] >= 15:
                time_limit = 2
            elif question['time'] >= 7.5:
                time_limit = 1

            self._questions.append(Question(
                question=question['question'],
                image_tags=question['image_description'],
                choices = question['choices'],
                correct=question['correct_index'],
                time_limit= time_limit,
                pontuation_system= 0
            ))

    @property
    def questions(self) -> List[Question]:
        return self._questions.copy()
    
    @property
    def title(self) -> str:
        return self._title
