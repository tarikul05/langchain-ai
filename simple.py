from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
import uuid

load_dotenv()

llm = init_chat_model("anthropic:claude-sonnet-4-20250514")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    llm_output: str | None
    decision: str | None

def chatbot(state: State) -> State:
    messages = state.get("messages", [])
    output = llm.invoke(messages)
    return {
        "messages": messages + [{"role": "assistant", "content": output.content}],
        "llm_output": output.content,
        "decision": None
    }

def human_approval(state: State) -> Command[Literal["approved_path", "rejected_path"]]:
    llm_output = state.get("llm_output", "")
    last_message = state["messages"][-1].content if state["messages"] else ""
    decision = interrupt({
        "question": "Do you approve the following output?",
        "llm_output": llm_output
    })
    if decision == "approve":
        return Command(goto="approved_path", update={"decision": "approved"})
    else:
        return Command(goto="rejected_path", update={"decision": "rejected"})

def approved_node(state: State) -> State:
    print("✅ Approved path taken.")
    return state

def rejected_node(state: State) -> State:
    print("❌ Rejected path taken.")
    return state

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("human_approval", human_approval)
graph_builder.add_node("approved_path", approved_node)
graph_builder.add_node("rejected_path", rejected_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "human_approval")
graph_builder.add_conditional_edges("human_approval", lambda state: state.get("decision"), {
    "approved": "approved_path",
    "rejected": "rejected_path"
})
graph_builder.add_edge("approved_path", END)
graph_builder.add_edge("rejected_path", END)

checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

def run_chat():
    state = {"messages": [], "llm_output": None, "decision": None}
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    while True:
        user_input = input("Your message: ")
        if not user_input.strip():
            print("Message cannot be empty.")
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting chat.")
            break
        state["messages"].append({"role": "user", "content": user_input})
        state = graph.invoke(state, config=config)
        # If interrupted for approval, resume with human input
        if "__interrupt__" in state:
            print("--- Human Approval Required ---")
            interrupt_value = state["__interrupt__"][0].value
            print(interrupt_value["question"])
            print("LLM Output:", interrupt_value["llm_output"])
            resume = input("Type 'approve' or 'reject': ").strip()
            state = graph.invoke(Command(resume=resume), config=config)
        # Show assistant output
        if state.get("llm_output"):
            print("Assistant:", state["llm_output"])
        if state.get("decision") == "approved":
            print("✅ Output approved.")
            break
        elif state.get("decision") == "rejected":
            print("❌ Output rejected.")
            break

if __name__ == "__main__":
    run_chat()