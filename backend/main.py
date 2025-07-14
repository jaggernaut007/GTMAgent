import logging
import logging.config
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import uuid4

from fastapi import FastAPI, Request, HTTPException, Header, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import the chat processor with the new history management
from chat_graph import process_message, clear_conversation, ChatManager

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": LOG_LEVEL
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "default",
            "level": LOG_LEVEL
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL
    }
})

# Create logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Startup Bakery API",
    description="API for the Startup Bakery chat application with conversation management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Log application startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Startup Bakery API server...")
    logger.info(f"Environment: {os.getenv('ENV', 'development')}")
    logger.info(f"Log level: {LOG_LEVEL}")

# Log application shutdown
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down Startup Bakery API server...")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat manager
chat_manager = ChatManager()

# Dependency to get or create conversation ID
def get_conversation_id(
    x_conversation_id: Optional[str] = Header(
        None, 
        description="Optional conversation ID. If not provided, a new one will be generated."
    )
) -> str:
    """Get or create a conversation ID from the header."""
    return x_conversation_id or f"conv_{uuid4().hex}"

# Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="The message content to process")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The assistant's response")
    conversation_id: str = Field(..., description="The ID of the current conversation")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: str = Field(..., description="ISO timestamp of the response")

class ConversationInfo(BaseModel):
    id: str = Field(..., description="Unique identifier for the conversation")
    created_at: str = Field(..., description="ISO timestamp of when the conversation was created")
    message_count: int = Field(..., description="Number of messages in the conversation")

# Root endpoint
@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Startup Bakery API. Let's start baking some dough!",
        "documentation": "/docs",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

# Chat endpoint
@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    chat_request: ChatRequest,
    conversation_id: str = Depends(get_conversation_id),
):
    """
    Process a chat message and return the assistant's response.
    
    Include the X-Conversation-ID header to continue an existing conversation.
    If not provided, a new conversation ID will be generated and returned.
    """
    logger.info(f"Processing chat message for conversation: {conversation_id}")
    logger.debug(f"Message content: {chat_request.message[:100]}..." if len(chat_request.message) > 100 else f"Message content: {chat_request.message}")
    
    try:
        start_time = datetime.utcnow()
        
        # Process the message with the conversation context
        response_message = process_message(
            message=chat_request.message,
            conversation_id=conversation_id
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Successfully processed message in {processing_time:.2f}s. "
            f"Conversation: {conversation_id}, "
            f"Response length: {len(response_message)}"
        )
        
        return {
            "response": response_message,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "error": None
        }
        
    except Exception as e:
        error_msg = f"Error processing chat message: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "response": "I'm sorry, I encountered an error processing your request.",
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Conversation management endpoints
@app.post("/conversations/{conversation_id}/clear", tags=["conversations"])
async def clear_conversation(conversation_id: str):
    """Clear the history of a specific conversation."""
    logger.info(f"Clearing conversation: {conversation_id}")
    try:
        clear_conversation(conversation_id)
        logger.info(f"Successfully cleared conversation: {conversation_id}")
        return {
            "status": "success",
            "message": f"Conversation {conversation_id} has been cleared",
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        error_msg = f"Error clearing conversation {conversation_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@app.get("/conversations", response_model=List[ConversationInfo], tags=["conversations"])
async def list_conversations():
    """List all active conversations with their metadata."""
    logger.info("Listing all active conversations")
    try:
        # In a real app, you might want to implement pagination here
        conversations = []
        for conv_id, processor in chat_manager.conversations.items():
            try:
                conversations.append({
                    "id": conv_id,
                    "created_at": next(
                        (msg.get("timestamp", "") 
                         for msg in processor.chat_history 
                         if msg.get("role") == "user"),
                        ""
                    ),
                    "message_count": len(processor.chat_history)
                })
            except Exception as e:
                logger.error(f"Error processing conversation {conv_id}: {str(e)}", exc_info=True)
                continue
                
        logger.info(f"Found {len(conversations)} active conversations")
        return conversations
        
    except Exception as e:
        error_msg = f"Error listing conversations: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@app.get("/health", tags=["system"])
async def health_check():
    """Check the health status of the API."""
    try:
        health_data = {
            "status": "healthy",
            "service": "startup-bakery",
            "timestamp": datetime.utcnow().isoformat(),
            "active_conversations": len(chat_manager.conversations),
            "environment": os.getenv("ENV", "development"),
            "version": "1.0.0"
        }
        
        logger.debug(f"Health check: {health_data}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health_data
        )
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV") == "development",
        log_level=LOG_LEVEL.lower(),
        access_log=True
    )
