from typing import Dict, List, TypedDict, Annotated, Literal, Optional
from operator import add
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the state for our chat application
class ChatState(TypedDict):
    messages: Annotated[list[dict], add]

class ChatProcessor:
    def __init__(self):
        # Initialize the LLM with GPT-4o-mini
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow for chat processing."""
        # Define the graph
        workflow = StateGraph(ChatState)
        
        # Add the LLM node
        workflow.add_node("llm", self._call_llm)
        
        # Set the entry point and define the flow
        workflow.set_entry_point("llm")
        workflow.add_edge("llm", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def _call_llm(self, state: ChatState) -> dict:
        """Call the LLM with the current conversation state."""
        # Convert to LangChain message format
        messages = []
        for msg in state["messages"]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                messages.append(SystemMessage(content=msg["content"]))
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Return the response in the expected format
        return {"messages": [{"role": "assistant", "content": response.content}]}
    
    def process_message(self, message: str, chat_history: Optional[list] = None) -> str:
        """
        Process a single message and return a response using LangGraph and GPT-4o-mini.
        
        Args:
            message: The user's message
            chat_history: Optional list of previous messages in the conversation
            
        Returns:
            The assistant's response
        """
        # Prepare the conversation history
        if chat_history is None:
            chat_history = []
        
        # Add the new user message
        messages = chat_history + [{"role": "user", "content": message}]
        
        # Run the workflow
        result = self.workflow.invoke({"messages": messages})
        
        # Extract the assistant's response
        response = result["messages"][-1]["content"]
        
        return response

# Create a global instance of the chat processor
chat_processor = ChatProcessor()

def process_message(message: str, chat_history: Optional[list] = None) -> str:
    """
    Process a single message and return a response using LangGraph and GPT-4o-mini.
    
    Args:
        message: The user's message
        chat_history: Optional list of previous messages in the conversation
        
    Returns:
        The assistant's response
    """
    return chat_processor.process_message(message, chat_history)
