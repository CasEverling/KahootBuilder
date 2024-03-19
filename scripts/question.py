from dataclasses import dataclass
from typing import List

@dataclass
class Question:
    question: str
    image_tags: str
    choices: List[str] 
    correct: int
    time_limit: int
    pontuation_system: int