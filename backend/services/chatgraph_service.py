"""
ChatGraph Service module.
Handles all LangGraph workflow and chat orchestration for GTM Agent.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Annotated, Optional, List

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langchain_community.tools.brave_search.tool import BraveSearch

from dotenv import load_dotenv
from utils.chat_utils import summarize_messages
from typing import TypedDict
# If you want full content:
import requests
from bs4 import BeautifulSoup
import json

MAX_TOKENS = 4000
load_dotenv()

class ChatState(TypedDict):
    messages: List[dict]
    needs_search: bool
    search_query: Optional[str]
    search_results: Optional[str]

def web_search(query: str) -> str:
    """Perform a web search using Brave Search and return results as a string with snippets and scraped page text for the first 5 results."""
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
    if not BRAVE_API_KEY:
        raise RuntimeError("BRAVE_API_KEY environment variable not set.")

    brave_search_tool = BraveSearch.from_api_key(BRAVE_API_KEY, search_kwargs={"count": 5})
    # Parse the Brave search results as JSON if needed
    raw_results = brave_search_tool.invoke(query)
    if isinstance(raw_results, str):
        results = json.loads(raw_results)
    else:
        results = raw_results

    output = []
    for idx, result in enumerate(results, 1):
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        page_text = ""
        if link:
            try:
                response = requests.get(link, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                page_text = soup.get_text(separator="\n", strip=True)
            except Exception as e:
                page_text = f"Could not retrieve page content: {e}"
        output.append(f"Result {idx}:\nTitle: {title}\nSnippet: {snippet}\nLink: {link}\nPage Content:\n{page_text}\n{'-'*40}")
    return "\n".join(output)

class ChatProcessor:
    def __init__(self, conversation_id: str = "default"):
        self.conversation_id = conversation_id
        self.logger = logging.getLogger(f"{__name__}.ChatProcessor.{conversation_id}")
        self.logger.debug("Initializing ChatProcessor.")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.6,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = [web_search]  # Pass the tool object, not the result of calling it
        self.workflow = self._build_workflow()
        self.chat_history = []
        self.logger.debug("ChatProcessor initialized.")
    def _decide_search_node(self, state: dict) -> dict:
        """Node to let the LLM decide if a web search is needed and what the query should be."""
        self.logger.info("Entering decide_search node.")
        messages = []
        for msg in state["messages"]:
            if isinstance(msg, type):
                self.logger.error(f"Found class object in messages: {msg}")
                continue
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                messages.append(SystemMessage(content=msg["content"]))

        # Add a system prompt to instruct the LLM to decide if a web search is needed
        system_prompt = (
            "You are an agent that decides if a web search is needed to answer the user's last question. "
            "If a search is needed, return a JSON object: {\"needs_search\": true, \"search_query\": \"...\"}. "
            "If not, return: {\"needs_search\": false, \"search_query\": null}. "
            "Only output the JSON object."
        )
        messages.append(SystemMessage(content=system_prompt))
        user_last = None
        for m in reversed(state["messages"]):
            if m["role"] == "user":
                user_last = m["content"]
                break
        if user_last:
            messages.append(HumanMessage(content=f"User's last message: {user_last}"))
        self.logger.debug(f"Messages for decide_search node: {messages}")
        response = self.llm.invoke(messages)
        self.logger.info(f"LLM decide_search response: {response.content}")
        import json
        try:
            decision = json.loads(response.content)
            state["needs_search"] = decision.get("needs_search", False)
            state["search_query"] = decision.get("search_query")
            self.logger.info(f"LLM decision: needs_search={state['needs_search']}, search_query={state['search_query']}")
        except Exception as e:
            self.logger.error(f"Failed to parse LLM decision for search: {e}, response: {response.content}")
            state["needs_search"] = False
            state["search_query"] = None
        self.logger.info("Exiting decide_search node.")
        return state
    def _web_search_node(self, state: dict) -> dict:
        self.logger.info("Entering web_search node.")
        query = state.get("search_query")
        if not query:
            self.logger.error("No search query provided for web search node.")
            state["search_results"] = None
            state["needs_search"] = False
            self.logger.info("Exiting web_search node (no query).");
            return state
        try:
            result = web_search(query)
            state["search_results"] = result
            state["needs_search"] = False
            self.logger.info(f"Web search result: {state['search_results']}")
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            state["search_results"] = None
            state["needs_search"] = False
        self.logger.info("Exiting web_search node.")
        return state

    def _build_workflow(self):
        self.logger.debug("Building workflow.")
        workflow = StateGraph(dict)
        # Add nodes: decide_search, web_search, llm
        workflow.add_node("decide_search", self._decide_search_node)
        workflow.add_node("web_search", self._web_search_node)
        workflow.add_node("llm", self._call_llm)
        # decide_search: if needs_search, go to web_search, else go to llm
        workflow.add_conditional_edges(
            "decide_search",
            lambda state: "web_search" if state.get("needs_search", False) else "llm"
        )
        # After web_search, always go to llm
        workflow.add_edge("web_search", "llm")
        # After llm, end
        workflow.set_finish_point("llm")
        workflow.set_entry_point("decide_search")
        compiled = workflow.compile()
        self.logger.debug("Workflow compiled.")
        return compiled

    def _call_llm(self, state: dict) -> dict:
        self.logger.info("Entering llm node.")
        try:
            self.logger.debug(f"Calling LLM with state: {state}")
            messages = []
            for msg in state["messages"]:
                if isinstance(msg, type):
                    self.logger.error(f"Found class object in messages: {msg}")
                    continue
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    messages.append(SystemMessage(content=msg["content"]))
            # If there are web search results, add them as a system message with clear instructions and readable formatting
            import json
            search_results = state.get("search_results")
            self.logger.debug(f"Search results: {search_results}")
            if search_results is not None :
                system_prompt = (
                    "Here are recent web search results. Use these to answer the user's question as best as possible. "
                    " Include a brief summary or highlight of current headlines drawn from the snippets provided, to add context to the answer."
                    "If you don't find an answer, say so. Results:\n" + search_results
                )
                messages.append(SystemMessage(content=system_prompt))
                self.logger.debug(f"Added formatted web search results to LLM messages: {search_results}")
            self.logger.debug(f"Messages for llm node: {messages}")
            response = self.llm.invoke(messages)
            self.logger.info(f"LLM llm node response: {response.content}")
            new_messages = [m for m in state["messages"] if not isinstance(m, type)] + [{
                "role": "assistant",
                "content": response.content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
            self.logger.info("Exiting llm node.")
            return {
                "messages": new_messages,
                "needs_search": state["needs_search"],
                "search_query": state["search_query"],
                "search_results": state["search_results"]
            }
        except Exception as e:
            self.logger.error(f"Error in _call_llm: {str(e)}", exc_info=True)
            raise

    def process_message(self, message: str) -> str:
        self.logger.info(f"Processing user message: {message}")
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.chat_history.append(user_message)
        processing_history = summarize_messages(self.llm, self.chat_history.copy(), MAX_TOKENS - 500)
        initial_state = {
            "messages": processing_history,
            "needs_search": False,
            "search_query": None,
            "search_results": None
        }
        self.logger.debug(f"Initial state for workflow: {initial_state}")
        result = self.workflow.invoke(initial_state)
        response = result["messages"][-1]["content"]
        assistant_message = result["messages"][-1]
        self.chat_history.append(assistant_message)
        self.logger.info(f"Assistant response: {response}")
        return response

    def clear_history(self):
        self.logger.info("Clearing chat history.")
        self.chat_history = []
