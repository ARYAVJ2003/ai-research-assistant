from  graph import build_graph

app = build_graph()


config = {
    "configurable": {
        "thread_id": "user1"
    }
}
while True:
    user_input = input("You: ")

    

    result = app.invoke({"input":user_input},config=config)

    print("AI:", result["output"])
    print("history:", result["history"])

    # 🔥 carry forward memory
    #state["history"] = result["history"]