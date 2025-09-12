Summarized conversation historyHere is a step-by-step explanation of the full code in main.py:

---

### 1. Imports and Setup
- Loads environment variables with `dotenv`.
- Imports types, LangChain/LangGraph modules, and utility libraries.
- Initializes the Claude Sonnet LLM via `init_chat_model`.

---

### 2. State Definition
- Defines a `State` TypedDict to track:
  - `messages`: List of AI/Human messages (can be objects or dicts).
  - `message_type`: Category of the conversation.
  - `decision`: Stores approval decision.
  - `show_ai_message`: Controls whether to display the AI response.

---

### 3. Email Approval Node
- `email_approval_node`: Checks if the last message contains an email.
- Extracts the email and asks the user to confirm its correctness (interrupt).
- Returns a command to route to either `approved_path` or `rejected_path` based on user input.

---

### 4. Terminal Nodes
- `approved_path`: Prints a thank you message and returns the state.
- `rejected_path`: Asks the user to provide their email again and returns the state.

---

### 5. Message Classifier
- `messageClassifier`: Pydantic model to classify messages into "Reivo", "Reivo-Bangladesh", or "Reivo-Japan".
- `classify_message`: Uses the LLM to classify the last human message and updates the state.

---

### 6. Router Node
- `router`: Routes the conversation to the appropriate node based on `message_type`.

---

### 7. Information Nodes
- `Reivo`: Provides general info about Reivo Inc and asks for an email if the topic is communication.
- `Reivo_Bangladesh`: Provides info about the Bangladesh office, team, and expertise.
- `Reivo_Japan`: Provides info about the Japan office, team, and expertise.

---

### 8. Email Utilities
- `contains_email`: Checks if a string contains an email address.
- `extract_email`: Extracts the first email address from a string.

---

### 9. Graph Construction
- Builds a `StateGraph` with all nodes.
- Adds edges for flow:
  - Start → classifier
  - classifier → email_approval (if email detected) or router
  - router → Reivo/Reivo-Bangladesh/Reivo-Japan
  - Info nodes → END
  - approved/rejected paths → END

---

### 10. Message Helpers
- `get_last_ai_message`: Gets the last AI message from the state.
- `last_human_message`: Gets the last human message from the state.

---

### 11. Chat Loop (`run_chat`)
- Initializes state and config.
- Loops to get user input.
- Appends user message to state.
- Invokes the graph to process the state.
- Handles interrupts (e.g., email approval) by prompting the user.
- Updates state and prints the assistant's response.

---

### 12. Main Entry Point
- Runs the chat loop if the script is executed directly.

---

**Summary:**  
This code builds a conversational chatbot using LangChain and LangGraph, with message classification, office-specific info, and a human-in-the-loop approval for email addresses. The workflow is managed as a graph, and the chat loop handles user interaction, state updates, and message display.