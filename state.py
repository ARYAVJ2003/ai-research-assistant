from typing import TypedDict

class State(TypedDict):
    input:str
    plan:list
    research:list
    output:str
    history:list