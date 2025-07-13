from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
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

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    try:
        # Log incoming request details
        print("\n=== Incoming Request ===")
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Headers: {request.headers}")
        print(f"Client: {request.client}")
        print(f"Request body: {await request.body()}")
        print(f"Parsed message: {chat_request}")
        
        # Process the message (you can add your chatbot logic here)
        response_message = f"I received your message: {chat_request.message}"

        # Prepare response
        response = {
            "response": response_message
        }
        
        # print("\n=== Sending Response ===")
        # print(f"Response: {response}")
        
        return response
        
    except Exception as e:
        # Log the error for debugging
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
