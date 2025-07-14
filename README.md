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

- Node.js (v14 or later)
- Python 3.9+ (recommended: 3.9 or later)
- npm or Yarn
- Git
- UV (Python package installer)

### Python Installation

#### macOS/Linux
1. **Install Python** (if not already installed):
   ```bash
   # Using Homebrew (macOS)
   brew install python
   
   # Or using system package manager (Ubuntu/Debian)
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Verify installation**:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Windows
1. **Download Python** from [python.org](https://www.python.org/downloads/)
2. **Run the installer** and make sure to check "Add Python to PATH"
3. **Verify installation** in Command Prompt or PowerShell:
   ```cmd
   python --version
   pip --version
   ```

### UV Installation

#### macOS/Linux
```bash
# Install uv using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to your shell's configuration file (e.g., ~/.bashrc, ~/.zshrc)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc  # or ~/.bashrc

# Verify installation
uv --version
```

#### Windows (PowerShell)
```powershell
# Install uv using PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Add uv to your PATH (if not added automatically)
[System.Environment]::SetEnvironmentVariable("Path", [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User) + ";$env:USERPROFILE\.cargo\bin", [System.EnvironmentVariableTarget]::User)

# Restart your terminal and verify installation
uv --version
```

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
uv run uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Start the Frontend

In a new terminal:

```bash
cd frontend
npm start
```

The frontend will open automatically at `http://localhost:3000`

## 🧪 Running Tests

### Backend Tests

To run the backend tests using `uv`, make sure you're in the backend directory:

```bash
cd backend

# Run all tests
uv run pytest tests/

# Run a specific test file
uv run pytest tests/test_main.py
uv run pytest tests/test_chat_graph.py

# Run tests with coverage report
uv run pytest --cov=. tests/

# Run tests with specific markers (if any)
uv run pytest -m "not slow" tests/  # Example: skip slow tests

# Run tests with verbose output
uv run pytest -v tests/
```

### Test Files

- `tests/test_main.py`: Tests for the FastAPI application endpoints
- `tests/test_chat_graph.py`: Tests for the chat graph functionality
- `tests/conftest.py`: Test fixtures and configurations

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
