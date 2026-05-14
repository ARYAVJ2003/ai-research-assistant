from typing import TypedDict


from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain.tools import tool
from state import State
import ast
from tools import web_search,calculator

load_dotenv(override=True)
#print("KEY:", os.getenv("GOOGLE_API_KEY"))

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

llm_with_tools=llm.bind_tools([web_search,calculator])
def planner(state: State):

    prompt = f"""
    Break the user request into clear research tasks.
STRICT RULES:
- One task = one objective
- NEVER combine explanation and calculation
- NEVER combine multiple topics
- Return ONLY valid Python list
- No extra text
- Maximum 3 tasks

GOOD EXAMPLES:

Input:
explain ai and calculate 10+2

Output:
["Explain AI",
 "Calculate 10+2"]

Input:
explain ai agents and types of machine learning

Output:
["Explain AI agents",
 "Explain types of machine learning"]

Input:
what is 5+3 and latest ai trends

Output:
["Calculate 5+3",
 "Explain latest AI trends"]

    User request:
    {state['input']}

  
    """

    result = llm.invoke(prompt)

    try:
        tasks = ast.literal_eval(result.content)

        # safety
        if not isinstance(tasks, list):
            tasks = [state["input"]]

    except:
        tasks = [state["input"]]

    fixed_tasks = []

    for task in tasks:

        if " and " in task.lower():

            split_tasks = task.split(" and ")

            fixed_tasks.extend(split_tasks)

        else:
            fixed_tasks.append(task)

    tasks = fixed_tasks

    print("\nPLAN:")
    print(tasks)

    return {"plan": tasks}

def researcher(state: State):

    results = []

    for task in state["plan"]:

        print("\nTASK:", task)

        prompt = f"""
        Previous conversation:
        {state.get('history', [])}

        Current task:
        {task}

        Use tools whenever needed.For summarization task dont use tool
        """

        response = llm_with_tools.invoke(prompt)

        # tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:

            for tool_call in response.tool_calls:

                if tool_call["name"] == "web_search":

                    tool_result = web_search.invoke(
                        tool_call["args"]
                    )

                    results.append(
                        f"WEB SEARCH: {tool_result}"
                    )

                elif tool_call["name"] == "calculator":

                    tool_result = calculator.invoke(
                        tool_call["args"]
                    )

                    results.append(
                        f"CALCULATION: {tool_result}"
                    )

        else:

            results.append(response.content[0]['text'])
    print( state.get('history', []))
    print("\nRESEARCH:")
    print(results)

    return {"research": results}


def writer(state: State):
    #print(state["research"])
    combined = "\n".join(state["research"])
    # 
    prompt = f"""

    You are a helpful AI research assistant.

    Previous conversation:
    {state.get('history', [])}

    Current research:
    {combined}

    Rules:
    - Give clear structured response
    - Use bullet points when useful
    - Keep calculations separate
    - Keep answer concise but informative
    """
    

    result = llm.invoke(prompt)

    history = state.get("history", [])

    history.append(f"User: {state['input']}")
    history.append(f"AI: {result.content[0]['text']}")

    return {
        "output": result.content[0]['text'],
        "history": history
    }
    


