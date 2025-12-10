import pytest
from main import app


class TestSimpleValidation:
    """Test basic validation - this actually tests YOUR code"""

    def test_create_todo_validation_empty_title(self, client):
        """Test that empty title is rejected"""
        response = client.post("/todos", json={"title": ""})
        assert response.status_code == 422
        assert "string_too_short" in response.json()["detail"][0]["type"]

    def test_create_todo_validation_missing_title(self, client):
        """Test that missing title is rejected"""
        response = client.post("/todos", json={"description": "No title"})
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "title"]
        assert error_detail["type"] == "missing"

    def test_health_endpoint_works(self, client):
        """Test health endpoint - simple smoke test"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint_works(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Welcome" in response.json()["message"]


class TestWithMockedDependency:
    """Test using FastAPI dependency override - the only mocking that actually works"""

    def test_create_todo_with_mock_service(self, client):
        """Test create todo with mocked service"""
        from unittest.mock import AsyncMock
        from app.services.todo_service import get_todo_service

        # Create mock service
        mock_service = AsyncMock()
        mock_service.create_todo.return_value = {
            "id": "mock-id-123",
            "title": "Mocked Todo",
            "description": "This comes from the mock",
            "completed": False,
        }

        # Override the dependency
        app.dependency_overrides[get_todo_service] = lambda: mock_service

        try:
            # Make request
            response = client.post(
                "/todos", json={"title": "Test Todo", "description": "Test Description"}
            )

            # Verify response
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Mocked Todo"
            assert data["id"] == "mock-id-123"

            # Verify mock was called
            mock_service.create_todo.assert_called_once()
            call_args = mock_service.create_todo.call_args[0][0]
            assert call_args.title == "Test Todo"
            assert call_args.description == "Test Description"

        finally:
            # Always clean up
            app.dependency_overrides.clear()

    def test_list_todos_with_mock_service(self, client):
        """Test list todos with mocked service"""
        from unittest.mock import AsyncMock
        from app.services.todo_service import get_todo_service

        mock_service = AsyncMock()
        mock_service.list_todos.return_value = [
            {"id": "1", "title": "Todo 1", "completed": False},
            {"id": "2", "title": "Todo 2", "completed": True},
        ]

        app.dependency_overrides[get_todo_service] = lambda: mock_service

        try:
            response = client.get("/todos")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "Todo 1"
            assert data[1]["completed"] == True

        finally:
            app.dependency_overrides.clear()


class TestSchemas:
    """Test your Pydantic schemas - this is YOUR validation logic"""

    def test_todo_create_schema(self):
        """Test TodoCreate validation"""
        from app.schemas.todo import TodoCreate

        # Valid todo
        todo = TodoCreate(title="Valid Todo", description="Valid description")
        assert todo.title == "Valid Todo"
        assert todo.description == "Valid description"

        # Invalid todo - empty title should fail
        with pytest.raises(ValueError):
            TodoCreate(title="", description="Description")

    def test_todo_update_schema(self):
        """Test TodoUpdate allows partial updates"""
        from app.schemas.todo import TodoUpdate

        # All fields
        update = TodoUpdate(title="New Title", completed=True, description="New desc")
        assert update.title == "New Title"
        assert update.completed == True

        # Just one field
        partial_update = TodoUpdate(completed=True)
        assert partial_update.completed == True
        assert partial_update.title is None  # Should be None for unset fields


class TestConfiguration:
    """Test your app configuration"""

    def test_settings_load(self):
        """Test that settings can be loaded"""
        from app.config import get_settings

        settings = get_settings()
        assert settings.mongo_uri.startswith("mongodb://")
        assert settings.mongo_db == "todo_db"
