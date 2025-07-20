from langchain_core.messages import HumanMessage
from typing import List, Dict, Any
import tiktoken
from datetime import datetime

def summarize_messages(llm, messages: list, max_tokens: int) -> list:
    """
    Summarize older messages if token limit is exceeded.
    Args:
        llm: The LLM instance to use for summarization.
        messages: List of Message objects (Pydantic models).
        max_tokens: Maximum allowed tokens.
    Returns:
        List of Message objects, with a summary if needed.
    """
    # All messages are dicts
    total_tokens = sum(count_tokens(m["content"]) + 4 for m in messages)
    if total_tokens <= max_tokens:
        return [m for m in messages if not isinstance(m, type)]

    split_idx = len(messages) // 2
    to_summarize = messages[:split_idx]
    to_keep = messages[split_idx:]

    summary_prompt = "Summarize the following conversation:\n\n"
    for m in to_summarize:
        summary_prompt += f"{m['role']}: {m['content']}\n"
    summary_prompt += "\nSummary:"

    summary = llm.invoke([HumanMessage(content=summary_prompt)]).content

    summary_message = {
        "role": "system",
        "content": f"Summary of earlier conversation: {summary}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    new_messages = [summary_message] + to_keep
    filtered_new_messages = [m for m in new_messages if not isinstance(m, type)]
    return summarize_messages(llm, filtered_new_messages, max_tokens) if total_tokens > max_tokens else filtered_new_messages


# Initialize tokenizer for the model we're using (gpt-4)
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string."""
    return len(tokenizer.encode(text))


def add_timestamps(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add timestamps to messages if they don't have them."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            **msg,
            "timestamp": msg.get("timestamp", now),
            "updated_at": now
        }
        for msg in messages
    ]
