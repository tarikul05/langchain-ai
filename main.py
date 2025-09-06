from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import  TypedDict   
# from langchain.document_loaders import TextLoader



load_dotenv()

llm = init_chat_model("anthropic:claude-sonnet-4-20250514")

class State(TypedDict):
  messages: Annotated[list, add_messages]
  message_type: str | None

class messageClassifier(BaseModel):
  message_type: Literal["Reivo-Bangladesh", "Reivo-Japan", "Reivo"] = Field(
    ...,
    description="Classify the user's message into one of the following categories: Reivo, Reivo-Bangladesh , Reivo-Japan"
  )

  def classify_message(state: State) -> str:
    last_message = state["messages"][-1]
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
        "content":  last_message.content
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
  last_message = state["messages"][-1]
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
"""
    },
    {
      "role": "user",
      "content":  last_message.content
    }
  ])

  return {"messages": [{ "role": "assistant", "content": reply.content }] , "message_type": state["message_type"]}

def Reivo_Bangladesh(state: State) -> State:
  last_message = state["messages"][-1]
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
      "content":  last_message.content
    }
  ])
  return {"messages": [{ "role": "assistant", "content": reply.content }] , "message_type": state["message_type"]}

def Reivo_Japan(state: State) -> State:
  last_message = state["messages"][-1]
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
      "content":  last_message.content
    }
  ])
  return {"messages": [{ "role": "assistant", "content": reply.content }] , "message_type": state["message_type"]}

graph_builder = StateGraph(State)
graph_builder.add_node("classifier", messageClassifier.classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("Reivo", Reivo)
graph_builder.add_node("Reivo-Bangladesh", Reivo_Bangladesh)
graph_builder.add_node("Reivo-Japan", Reivo_Japan)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges("router", lambda state: state.get("next"), {"Reivo": "Reivo", "Reivo-Bangladesh": "Reivo-Bangladesh", "Reivo-Japan": "Reivo-Japan"})
graph_builder.add_edge("Reivo", END)
graph_builder.add_edge("Reivo-Bangladesh", END)
graph_builder.add_edge("Reivo-Japan", END)

graph = graph_builder.compile()


def run_chat():
   state = {"messages": [], "message_type": None}
   while True:
      user_input = input("Your message: ")
      if user_input == "exit":
         print("Exiting chat.")
         break
      state["messages"].append({"role": "user", "content": user_input})
      state = graph.invoke(state)
      last_message = state["messages"][-1].content
      type = state["message_type"]
      print(f"💪Assistant ({type}): {last_message}")
      print("----------------------------------------------------------------------------------------------------------------------")

      
if __name__ == "__main__":
  run_chat()