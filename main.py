from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import  TypedDict   
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
import uuid
import re
from langchain_core.messages import AIMessage, HumanMessage
from typing import Union
# from langchain.document_loaders import TextLoader

load_dotenv()
llm = init_chat_model("anthropic:claude-sonnet-4-20250514")



class State(TypedDict):
  messages: Annotated[list[Union[AIMessage, HumanMessage, dict]], add_messages]
  message_type: str | None
  decision: str | None
  show_ai_message: bool | None

# Interrupt node for email approval
def email_approval_node(state: State) -> Command[Literal["approved_path", "rejected_path"]]:
  # print("=== Email Approval Node Invoked ===")
  email = extract_email(state["messages"][-1].content)
  decision = interrupt({
    "question": "{email}  this  email address is correct ?".format(email=email),
    "email": email
  })
  if decision == "yes":
    return Command(goto="approved_path", update={"decision": "yes"})
  else:
    return Command(goto="rejected_path", update={"decision": "no"})

# Terminal nodes for approval/rejection
def approved_path(state: State) -> State:
  print("✅ Thank you! We will reach out to you soon via the provided email address.")
  return state

def rejected_path(state: State) -> State:
  print("❌ I'm sorry for the inconvenience. Please provide your email address again.")
  return state

class messageClassifier(BaseModel):
  message_type: Literal["Reivo-Bangladesh", "Reivo-Japan", "Reivo"] = Field(
    ...,
    description="Classify the user's message into one of the following categories: Reivo, Reivo-Bangladesh , Reivo-Japan"
  )

  def classify_message(state: State) -> str:
    classifier_llm = llm.with_structured_output(messageClassifier)
    result = classifier_llm.invoke([
      {
        "role": "system",
        "content": """
You are a helpful assistant that classifies messages into categories.
The categories are:
1. Reivo-Bangladesh
2. Reivo-Japan
If the message is related to Bangladesh office, classify it as "Reivo-Bangladesh".
If the message is related to Japan office, classify it as "Reivo-Japan".
If the message is related to Reivo in general, classify it as "Reivo".
"""
      },
      {
        "role": "user",
        "content":  last_human_message(state)
      }
    ])
    return {"message_type": result.message_type}

def router(state: State) -> State:
  message_type = state.get("message_type", "Reivo")
  if message_type == "Reivo-Bangladesh":
    return {"next": "Reivo-Bangladesh"}
  elif message_type == "Reivo-Japan":
    return {"next": "Reivo-Japan"}
  else:
    return {"next": "Reivo"}
  

def Reivo(state: State) -> State:
  reply = llm.invoke([
    {
      "role": "system",
      "content": """
You are a helpful assistant that provides information about Reivo Inc.
Reivo Inc is a technology company that provides software development services and IT solutions to businesses worldwide.
Reivo Inc specializes in web and mobile application development, cloud computing, AI and machine learning, and digital transformation.
Reivo Inc is headquartered in Tokyo, Japan, with offices in Bangladesh and other countries.
Reivo Inc's mission is to help businesses leverage technology to achieve their goals and stay competitive in the digital age.
Reivo Inc's core values are innovation, quality, customer satisfaction, and teamwork.
Reivo Inc's clients include startups, SMEs, and large enterprises across various industries such as finance, healthcare, e-commerce, education, and more.
Reivo Inc's services include custom software development, IT consulting, project management, quality assurance, and support and maintenance.
Reivo Inc's team consists of experienced software engineers, designers, project managers, and business analysts who are passionate about technology and delivering value to clients.
If the user message is related to communication ask him for his email address for meeting scheduling.
"""
    },
    {
      "role": "user",
      "content":  last_human_message(state)
    }
  ])

  return {"messages": [AIMessage(content=reply.content)] , "message_type": state["message_type"]}

def Reivo_Bangladesh(state: State) -> State:
  reply = llm.invoke([
    {
      "role": "system",
      "content": """
You are a helpful assistant that provides information about Reivo Inc's Bangladesh office.
Reivo Inc's Bangladesh office is located in Dhaka, the capital city of Bangladesh.
The office address is: Wakil Tower (8th floor), Ta-131, Gulshan - Badda link road, Dhaka - 1212, Bangladesh.
The Bangladesh office is headed by Mr. Tarikul Islam, who is the Team Leader & Project manager at Reivo Inc.
The Bangladesh office has a team of skilled software developers, designers, and project managers who work on various projects for Reivo Inc's clients.
The Bangladesh office specializes in web and mobile application development, cloud computing, and IT solutions.
The Bangladesh office is known for its expertise in technologies such as PHP, Laravel, Ruby on Rails, DevOps, Nuxt, Vue, Javascript, Node, React Native, AWS, MySQL, PostgreSQL, Flutter, Docker, GitHub Actions, Jenkins, and CI/CD.
The Bangladesh office is committed to delivering high-quality software solutions and excellent customer service to clients.
Bangladesh office team members include:
1. Tarikul Islam - Team Leader & Project manager
2. Ashraful Ratul - Senior Software Engineer
3. Shajalal - Software Engineer
Tarikul Islam's speciality is Team Leader & Project manager at Reivo Inc with PHP | Laravel | Ruby On Rails | DevOps | Nuxt | Vue | Javascript | Node| React Native | AWS | MYSQL | PostgreSQL | Flutter | Docker | Github action | Jenkins | CI/CD
Ashraful Ratul's speciality is Full Stack Developer at Reivo Inc with PHP | Laravel | Ruby On Rails | DevOps | Nuxt | Vue | Javascript | Node| React Native | AWS | MYSQL | PostgreSQL | Flutter | Docker | Github action | Jenkins | CI/CD
Shajalal's speciality is Full Stack Developer at Reivo Inc with PHP | Laravel | Ruby | frontend | Nuxt | Vue | Javascript | Node| React Native | AWS | MYSQL | PostgreSQL | vue | react
"""
    },
    {
      "role": "user",
      "content":  last_human_message(state)
    }
  ])
  return {"messages": [AIMessage(content=reply.content)] , "message_type": state["message_type"]}

def Reivo_Japan(state: State) -> State:
  reply = llm.invoke([
    {
      "role": "system",
      "content": """
You are a helpful assistant that provides information about Reivo Inc's Japan office.

Reivo Inc's Japan office and headquarters are located in Tokyo, Japan.
The office address is: 1-2-3 Shibuya, Shibuya-ku, Tokyo 150-0002, Japan.
The Japan office is headed by Mr. Hiroshi Tanaka, who is the Team Leader & Project manager at Reivo Inc.
The Japan office has a team of skilled software developers, designers, and project managers who work on various projects for Reivo Inc's clients.
The Japan office specializes in web and mobile application development, cloud computing, and IT solutions.
The Japan office is known for its expertise in technologies such as PHP, Laravel, Ruby on Rails, DevOps, Nuxt, Vue, Javascript, Node, React Native, AWS, MySQL, PostgreSQL, Flutter, Docker, GitHub Actions, Jenkins, and CI/CD.
The Japan office is committed to delivering high-quality software solutions and excellent customer service to clients.
Japan office team members include:
1. Keita Ashihara - CEO & Founder
2. Mitsutoshi, Watanabe - CTO & Co-Founder
3. Takashi Seino - Project Manager
4. Ko Nitta - Project Manager of Bangladesh Office

"""
    },
    {
      "role": "user",
      "content":  last_human_message(state)
    }
  ])
  return {"messages": [AIMessage(content=reply.content)] , "message_type": state["message_type"]}


def contains_email(text):
  return re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text) is not None

# write a function that will extract email from text
def extract_email(text):
  match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
  return match.group(0) if match else None

graph_builder = StateGraph(State)
graph_builder.add_node("classifier", messageClassifier.classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("Reivo", Reivo)
graph_builder.add_node("Reivo-Bangladesh", Reivo_Bangladesh)
graph_builder.add_node("Reivo-Japan", Reivo_Japan)
graph_builder.add_node("email_approval", email_approval_node)
graph_builder.add_node("approved_path", approved_path)
graph_builder.add_node("rejected_path", rejected_path)

graph_builder.add_edge(START, "classifier")
# Conditional edge from classifier to email_approval if email detected, else router
graph_builder.add_conditional_edges(
  "classifier",
  lambda state: "email_approval" if contains_email(state["messages"][-1].content) else "router",
  {
    "email_approval": "email_approval",
    "router": "router"
  }
)
graph_builder.add_conditional_edges("router", lambda state: state.get("next"), {"Reivo": "Reivo", "Reivo-Bangladesh": "Reivo-Bangladesh", "Reivo-Japan": "Reivo-Japan"})
graph_builder.add_edge("Reivo", END)
graph_builder.add_edge("Reivo-Bangladesh", END)
graph_builder.add_edge("Reivo-Japan", END)
graph_builder.add_edge("approved_path", END)
graph_builder.add_edge("rejected_path", END)

checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)


def get_last_ai_message(state):
  for msg in reversed(state["messages"]):
      if isinstance(msg, dict) and msg.get("role") == "assistant":
          return msg.get("content", "")
      elif isinstance(msg, AIMessage):
          return msg.content
  return None

def last_human_message(state):
  for msg in reversed(state["messages"]):
      if isinstance(msg, dict) and msg.get("role") == "user":
          return msg.get("content", "")
      elif isinstance(msg, HumanMessage):
          return msg.content
  return None

def run_chat():
  config = {"configurable": {"thread_id": str(uuid.uuid4())}}
  state = {"messages": [], "message_type": None, "decision": None, "show_ai_message": True}
  while True:
    user_input = input("Your message: ")
    if user_input == "exit":
      print("Exiting chat.")
      break
    state["messages"].append(HumanMessage(content=user_input))
    result = graph.invoke(state, config=config)
    # check for interrupt
    while True:
      if result.get("__interrupt__", False):
        interrupt_obj = result.get("__interrupt__")
        if isinstance(interrupt_obj, list) and len(interrupt_obj) > 0:
            interrupt_data = interrupt_obj[0].value
            print(interrupt_data.get("question", ""))
        elif hasattr(interrupt_obj, "value"):
            interrupt_data = interrupt_obj.value
            print(interrupt_data.get("question", ""))
        else:
            print(interrupt_obj)
        resume = input("Type 'yes' or 'no': ").strip()
        result = graph.invoke(Command(resume=resume), config=config)
        result.update({"show_ai_message": False})
      else:
        break
    state = result
    # Print assistant response if available
    if state.get("messages") and len(state["messages"]) > 0 and state.get("show_ai_message", True):
      last_message = get_last_ai_message(state)
      type = state.get("message_type", "")
      print(f"💪Assistant ({type}): {last_message}")
      print("----------------------------------------------------------------------------------------------------------------------")

      
if __name__ == "__main__":
  run_chat()

