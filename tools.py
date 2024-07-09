from typing import Callable
from pydantic import BaseModel

class ToolChoice(BaseModel):
    tool_name: str
    reason_of_choice: str

class Tool:
    def __init__(self, name: str, func: Callable) -> None:
        self.name = name
        self.func = func

    def act(self, **kwargs) -> str:
        return self.func(**kwargs)