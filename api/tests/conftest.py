"""Pytest fixtures for API testing."""

import contextlib
import os
import sys

# Add api directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment BEFORE any imports
os.environ["DATABASE_URL"] = "sqlite:///./test_data.db"
os.environ["DEBUG"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

# Clear any cached settings
from config import get_settings  # noqa: E402

get_settings.cache_clear()

from db import engine  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create fresh database tables for each test."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)
    # Clean up test database file
    if os.path.exists("./test_data.db"):
        with contextlib.suppress(OSError):
            os.remove("./test_data.db")


@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_task():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "A test task description",
        "priority": "normal",
    }


@pytest.fixture
def sample_task_high_priority():
    """Sample high priority task data."""
    return {
        "title": "Urgent Task",
        "description": "This is urgent",
        "priority": "high",
    }


@pytest.fixture
def sample_task_with_due_date():
    """Sample task with due date."""
    return {
        "title": "Task with deadline",
        "priority": "normal",
        "due_date": "2025-12-31T23:59:59",
    }


@pytest.fixture
def sample_task_with_tags():
    """Sample task with tags."""
    return {
        "title": "Tagged Task",
        "priority": "normal",
        "tags": "urgent, project",
    }


@pytest.fixture
def sample_task_recurring():
    """Sample recurring task."""
    return {
        "title": "Daily Standup",
        "priority": "normal",
        "recurrence": "daily",
    }
