# FastAPI Todo Application

A FastAPI-based todo application with MongoDB integration using Beanie ODM.

## Project Setup

### Prerequisites

- Python 3.12+
- MongoDB (local or cloud)
- UV (Python package manager)

### Initial Setup

1. **Install UV (if not already installed)**

   ```bash
   # On Windows (PowerShell)
   iwr https://astral.sh/uv/install.ps1 | iex

   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Initialize the project**

   ```bash
   # Create project directory
   mkdir fastapi-todos
   cd fastapi-todos

   # Initialize UV project
   uv init
   ```

3. **Add project dependencies**

   ```bash
   # Add main dependencies
   uv add fastapi
   uv add beanie
   uv add motor
   uv add uvicorn

   # Add development dependencies
   uv add --dev pytest
   uv add --dev pytest-asyncio
   uv add --dev httpx
   ```

## Running the Application

### Start the development server

```bash
uv run python main.py
```

Or using uvicorn directly:

```bash
uv run uvicorn main:app --reload
```

The application will be available at:

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Environment Configuration

Create a `.env` file in the project root (optional):

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=todo_db
```

## Testing

### Run all tests

```bash
uv run pytest
```

### Run tests with verbose output

```bash
uv run pytest -v
```

### Run specific test file

```bash
uv run pytest tests/test_todos.py
```

### Run tests with coverage

```bash
uv add --dev pytest-cov
uv run pytest --cov=app
```

## Project Structure

```
fastapi-todos/
├── main.py                 # Application entry point
├── pyproject.toml          # Project configuration
├── .python-version         # Python version specification
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── db.py               # Database initialization
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py         # Todo document model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── todo.py         # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_service.py # Business logic
│   └── routers/
│       ├── __init__.py
│       └── todo_router.py  # API endpoints
└── tests/
    ├── __init__.py
    ├── conftest.py         # Test configuration
    └── test_todos.py       # Test cases
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /todos` - List all todos
- `POST /todos` - Create a new todo
- `GET /todos/{todo_id}` - Get a specific todo
- `PUT /todos/{todo_id}` - Update a todo
- `DELETE /todos/{todo_id}` - Delete a todo

## Development Commands

### Package Management

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a package
uv remove package-name

# Update all packages
uv lock --upgrade

# Install dependencies from pyproject.toml
uv sync
```

### Git Workflow

```bash
# Create and switch to develop branch
git checkout -b develop

# Push develop branch to remote
git push --set-upstream origin develop

# Switch between branches
git checkout main
git checkout develop
```

## Technology Stack

- **FastAPI** - Modern web framework for Python APIs
- **Beanie** - Async MongoDB ODM based on Pydantic
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation and serialization
- **UV** - Fast Python package manager
- **Pytest** - Testing framework
- **MongoDB** - NoSQL database

## Features

- ✅ CRUD operations for todos
- ✅ Data validation with Pydantic
- ✅ Async/await support
- ✅ Automatic API documentation
- ✅ Type hints throughout
- ✅ Comprehensive testing
- ✅ Modern dependency management with UV
- ✅ Clean architecture with separation of concerns

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Add tests for new functionality
4. Run tests: `uv run pytest`
5. Create a pull request to `develop`
