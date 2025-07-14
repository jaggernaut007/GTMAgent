from typing import List, Dict, Any
import tiktoken
from datetime import datetime

# Initialize tokenizer for the model we're using (gpt-4)
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string."""
    return len(tokenizer.encode(text))

def truncate_messages(messages: List[Dict[str, str]], max_tokens: int = 4000) -> List[Dict[str, str]]:
    """
    Truncate messages to fit within the token limit while preserving the most recent messages.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        max_tokens: Maximum number of tokens to keep (default: 4000 for gpt-4 with some buffer)
        
    Returns:
        Truncated list of messages that fits within the token limit
    """
    total_tokens = 0
    truncated_messages = []
    
    # Process messages in reverse order (newest first)
    for message in reversed(messages):
        message_tokens = count_tokens(message["content"])
        
        # Add some buffer for message formatting tokens
        message_tokens_with_buffer = message_tokens + 4  # 4 tokens for role/formatting
        
        if total_tokens + message_tokens_with_buffer > max_tokens:
            # If adding this message would exceed the limit, stop adding more
            break
            
        truncated_messages.append(message)
        total_tokens += message_tokens_with_buffer
    
    # Return messages in original order (oldest first)
    return list(reversed(truncated_messages))

def add_timestamps(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add timestamps to messages if they don't have them."""
    now = datetime.utcnow().isoformat()
    return [
        {
            **msg,
            "timestamp": msg.get("timestamp", now),
            "updated_at": now
        }
        for msg in messages
    ]
