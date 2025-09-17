# Employee Management API

A production-ready FastAPI application for managing employee records with MongoDB integration.

## Features

- **CRUD Operations**: Create, Read, Update, Delete employee records
- **JWT Authentication**: Secure authentication for protected operations
- **Advanced Querying**: Filter by department, search by skills
- **Pagination**: Optional pagination for large datasets
- **Auto-generated IDs**: Employee IDs are automatically generated (E001, E002, etc.)
- **Comprehensive Testing**: Full test coverage with pytest
- **Docker Support**: Containerized application with Docker Compose

## Local Development Setup

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- UV package manager (recommended) or pip

### Setup

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/takshch/fastapi-example
   cd fastapi-example
   pip install -e .
   ```

2. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker compose up -d  # or uvicorn main:app --reload for local development
   ```

4. **Access the application**
   - API: http://localhost:8000
   - **Swagger UI: http://localhost:8000/docs** (for API documentation)
   - Health Check: http://localhost:8000/health

## Development Commands

```bash
# Install dependencies
pip install -e .                    # Production dependencies
pip install -e ".[dev]"             # Development dependencies

# Run tests
pytest tests/ --cov=app            # Run all tests with coverage

# Code quality
flake8 app/ tests/ main.py         # Run linting checks
black app/ tests/ main.py          # Format code
isort app/ tests/ main.py          # Sort imports

# Docker operations
docker compose up -d               # Start containers
docker compose down                # Stop containers
docker compose logs -f app         # View application logs

# Database
docker compose exec app python scripts/seed_data.py  # Seed database
```

## API Documentation

**For complete API documentation, run the application and visit: http://localhost:8000/docs**

The API includes:
- **Authentication**: Register and login endpoints
- **Employee CRUD**: Create, read, update, delete operations
- **Search & Filter**: Search by skills, filter by department
- **Pagination**: Optional pagination for all list endpoints
- **JWT Authentication**: Protected endpoints require Bearer token

## Testing

```bash
pytest tests/ --cov=app  # Run all tests with coverage
```

## License

MIT License
