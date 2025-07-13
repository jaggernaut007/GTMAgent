from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from chat_graph import process_message

app = FastAPI(title="Startup Bakery API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Startup Bakery. Let's start baking some dough!"}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

# In-memory conversation history (in a real app, use a database)
conversation_history = {}

def get_conversation_id(request: Request) -> str:
    """Generate a unique ID for each conversation based on client IP."""
    client = request.client
    return f"{client.host}:{client.port}" if client else "default"

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    try:
        # Get or create conversation history for this client
        conv_id = get_conversation_id(request)
        if conv_id not in conversation_history:
            conversation_history[conv_id] = []
        
        # Log the incoming message
        print(f"\n=== Message from {conv_id} ===")
        print(f"Message: {chat_request.message}")
        
        # Process the message using our chat processor
        response_message = process_message(chat_request.message)
        
        # Log the response
        print(f"Response: {response_message}")
        
        return {"response": response_message}
        
    except Exception as e:
        error_msg = f"Error processing chat message: {str(e)}"
        print(f"\n!!! ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "response": "I'm sorry, I encountered an error processing your request.",
                "error": str(e)
            }
        )

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "startup-bakery"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
