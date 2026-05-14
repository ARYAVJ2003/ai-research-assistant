from langgraph.graph import StateGraph
from state import State
from nodes import  planner,researcher,writer
from langgraph.checkpoint.memory import MemorySaver

def build_graph():
    graph=StateGraph(State)
    graph.add_node("planner",planner)
    graph.add_node("researcher",researcher)
    graph.add_node("writer",writer)
    graph.add_edge("planner","researcher")
    graph.add_edge("researcher","writer")
    graph.set_entry_point("planner")
    graph.set_finish_point("writer")
    memory=MemorySaver()
    return graph.compile(checkpointer=memory)
