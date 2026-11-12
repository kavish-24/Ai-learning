from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

load_dotenv()

model = init_chat_model("groq:openai/gpt-oss-20b")
SUMMARIZE=5
keep_last=2

class Replace(list):
    """Marker: 'replace the list' instead of 'append to it'."""

def append_messages(old: list, new: list) -> list:
    if isinstance(new, Replace):
        return list(new)
    return old + new


class ChatState(TypedDict):
    messages: Annotated[list, append_messages]
    summary:str
    turns:int

def to_text(messages: list) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

def chatbot(state: ChatState):
    prompt=[]
    if state.get("summary"):
        prompt.append({"role":"system","content":f"Summary of previous conversation: {state['summary']}"})
        
    prompt+=state["messages"]
    reply = model.invoke(prompt)
    return {"messages": [{"role": "assistant", "content": reply.content}],
            "turns": state["turns"] + 1,
            }

def summarize(state: ChatState):
    summary_prompt = [{"role":"system","content":"Summarize the following conversation in a few sentences."}]
    summary_prompt += state["messages"]
    reply = model.invoke(summary_prompt)
    return {"summary": reply.content,
            "messages": Replace(state["messages"][-keep_last:]),
            "turns": 0,
            }
    
def should_summarize(state: ChatState):
    return state["turns"] >= SUMMARIZE

def final_summary(state:ChatState):
    if not state["messages"] and not state["summary"]:
        print("No conversation to summarize.")
        return
    prompt=(
        f"Final summary of the conversation:\n{state['summary']}\n\n"
        f"Conversation:\n{to_text(state['messages'])}\n\n"
        "Please provide a concise summary of the entire conversation."
    )
    print("\n===== OVERALL SUMMARY =====")
    for chunk in model.stream([{"role": "user", "content": prompt}]):
        print(chunk.content, end="", flush=True)
    print("\n===========================")

builder = StateGraph(ChatState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
graph = builder.compile()


def main():
    state = {"messages": [], "summary": "", "turns": 0}
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit"]:
            break
        if not user_input:
            continue
        state["messages"]=state["messages"]+[
{"role": "user", "content": user_input}
        ]
        print("Bot: ", end="", flush=True)
        for mode , data in graph.stream(state, stream_mode=["messages", "values"]):
            if mode=="messages":
                chunk , meta= data
                if meta["langgraph_node"] == "chatbot":   # skip summarize tokens
                    print(chunk.content, end="", flush=True)
            else:
                state=data
                
        print()
        final_summary(state)


if __name__ == "__main__":
    main()
