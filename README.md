# 🚀 Startup Bakery

An agentic AI chat assistant, designed to help you bake your next successful startup idea.

## 🍰 Features

- **Backend API** built with FastAPI
  - RESTful endpoints
  - Async support
  - Automatic API documentation
  - Health check endpoint

- **Frontend** built with React & TypeScript
  - Responsive chat interface
  - Real-time messaging
  - Modern UI with styled-components
  - Type-safe development

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, Uvicorn, Langgraph
- **Frontend**: React, TypeScript
- **Build Tools**: npm, Create React App
- **API Documentation**: Swagger UI, ReDoc

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or Yarn
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd startup-bakery
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uv pip install .
   cp .env-example .env
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   # or
   yarn install
   ```

## 🏃‍♂️ Running the Application

### Start the Backend

```bash
cd backend
source .venv/bin/activate && uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Start the Frontend

In a new terminal:

```bash
cd frontend
npm start
```

The frontend will open automatically at `http://localhost:3000`

## 🤖 Chat System Architecture

The chat system is built with a modular and scalable architecture that enables stateful conversations and complex interactions. Here are the key components:

### 🏗 Core Components

#### Chat Graph
- **LangGraph-based** state machine for managing conversation flow
- **Stateful processing** with conversation context preservation
- **Modular design** for easy extension of capabilities
- **Token management** with intelligent message truncation

#### Chat Manager
- **Conversation lifecycle** management
- **Thread-safe** conversation handling
- **Global state** management for multi-user support
- **Conversation isolation** for security and privacy

#### Chat Processing
- **Asynchronous** message processing pipeline
- **Context window management** with smart truncation
- **Token counting** for efficient resource usage
- **Timestamp management** for message ordering

### 🔄 Conversation Flow
1. User sends a message to the `/chat` endpoint
2. System retrieves or creates a conversation context
3. Message is processed through the chat graph
4. Response is generated using GPT-4o-mini
5. Conversation state is updated and persisted

### 🎛 API Endpoints
- `POST /chat` - Process a chat message
- `DELETE /conversations/{conversation_id}` - Clear a conversation
- `GET /conversations` - List all active conversations
- `GET /health` - Check API health status

### 🛠 Technical Details
- **State Management**: Thread-safe conversation state tracking
- **Token Management**: Automatic truncation of long conversations
- **Error Handling**: Comprehensive error handling and logging
- **Scalability**: Designed for horizontal scaling

## 🌐 API Documentation

Once the backend is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗 Project Structure

```
startup-bakery/
├── backend/           # FastAPI backend
│   ├── main.py       # Main application file
│   ├── tests/        # Test files
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.tsx
│   │   └── index.tsx
│   └── package.json
└── README.md         # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

Have questions? Open an issue or reach out to the maintainers.
