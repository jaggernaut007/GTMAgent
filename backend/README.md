# Startup Bakery - Backend

A FastAPI-based backend service for the Startup Bakery platform. This service provides the API endpoints needed to power the frontend application.

## Features

- RESTful API endpoints
- Health check endpoint
- Ready for extension with business logic
- Built with FastAPI for high performance

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Poetry (recommended) or pip for dependency management

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd startup-bakery/backend
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   # Using Poetry (recommended)
   poetry install

   # OR using pip
   pip install -r requirements.txt
   ```

4. Set up environment variables (if any):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Running the Server

### Development

To run the development server with auto-reload:

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`

### Production

For production, use a production-grade ASGI server like Uvicorn with Gunicorn:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Available Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint

## Testing

To run the test suite:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
