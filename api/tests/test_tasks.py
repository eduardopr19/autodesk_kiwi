"""Unit tests for Tasks API endpoints."""

from fastapi import status


class TestTasksCRUD:
    """Tests for basic CRUD operations on tasks."""

    def test_create_task(self, client, sample_task):
        """Test creating a new task."""
        response = client.post("/tasks", json=sample_task)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == sample_task["title"]
        assert data["description"] == sample_task["description"]
        assert data["priority"] == sample_task["priority"]
        assert data["status"] == "todo"
        assert data["id"] is not None

    def test_create_task_minimal(self, client):
        """Test creating a task with minimal data."""
        response = client.post("/tasks", json={"title": "Minimal task"})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Minimal task"
        assert data["priority"] == "normal"

    def test_create_task_with_priority(self, client, sample_task_high_priority):
        """Test creating a task with high priority."""
        response = client.post("/tasks", json=sample_task_high_priority)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["priority"] == "high"

    def test_create_task_with_due_date(self, client, sample_task_with_due_date):
        """Test creating a task with due date."""
        response = client.post("/tasks", json=sample_task_with_due_date)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["due_date"] is not None

    def test_create_task_with_tags(self, client, sample_task_with_tags):
        """Test creating a task with tags."""
        response = client.post("/tasks", json=sample_task_with_tags)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["tags"] == "urgent, project"

    def test_create_task_with_recurrence(self, client, sample_task_recurring):
        """Test creating a recurring task."""
        response = client.post("/tasks", json=sample_task_recurring)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["recurrence"] == "daily"

    def test_create_task_invalid_priority(self, client):
        """Test creating a task with invalid priority fails."""
        response = client.post("/tasks", json={
            "title": "Bad task",
            "priority": "invalid"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_empty_title(self, client):
        """Test creating a task with empty title fails."""
        response = client.post("/tasks", json={"title": ""})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_task(self, client, sample_task):
        """Test getting a specific task."""
        # Create task first
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        # Get the task
        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == task_id
        assert response.json()["title"] == sample_task["title"]

    def test_get_task_not_found(self, client):
        """Test getting a non-existent task returns 404."""
        response = client.get("/tasks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_tasks(self, client, sample_task):
        """Test listing all tasks."""
        # Create some tasks
        client.post("/tasks", json=sample_task)
        client.post("/tasks", json={"title": "Second task"})

        response = client.get("/tasks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_tasks_empty(self, client):
        """Test listing tasks when none exist."""
        response = client.get("/tasks")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_update_task_title(self, client, sample_task):
        """Test updating a task's title."""
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"title": "Updated title"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Updated title"

    def test_update_task_status(self, client, sample_task):
        """Test updating a task's status."""
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"status": "doing"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "doing"

    def test_update_task_to_done(self, client, sample_task):
        """Test marking a task as done sets completed_at."""
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"status": "done"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "done"
        assert response.json()["completed_at"] is not None

    def test_update_task_not_found(self, client):
        """Test updating a non-existent task returns 404."""
        response = client.put("/tasks/99999", json={"title": "Updated"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task(self, client, sample_task):
        """Test deleting a task."""
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        response = client.delete(f"/tasks/{task_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify task is deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_not_found(self, client):
        """Test deleting a non-existent task returns 404."""
        response = client.delete("/tasks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTasksFiltering:
    """Tests for filtering and sorting tasks."""

    def test_filter_by_status(self, client):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        client.post("/tasks", json={"title": "Todo task"})
        task2_response = client.post("/tasks", json={"title": "Doing task"})
        client.put(f"/tasks/{task2_response.json()['id']}", json={"status": "doing"})

        response = client.get("/tasks?status=doing")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "doing"

    def test_filter_by_priority(self, client):
        """Test filtering tasks by priority."""
        client.post("/tasks", json={"title": "Normal task", "priority": "normal"})
        client.post("/tasks", json={"title": "High task", "priority": "high"})

        response = client.get("/tasks?priority=high")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "high"

    def test_search_by_title(self, client):
        """Test searching tasks by title."""
        client.post("/tasks", json={"title": "Buy groceries"})
        client.post("/tasks", json={"title": "Clean house"})

        response = client.get("/tasks?q=groceries")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert "groceries" in data[0]["title"].lower()

    def test_sort_by_created_at_desc(self, client):
        """Test sorting tasks by creation date descending."""
        client.post("/tasks", json={"title": "First task"})
        client.post("/tasks", json={"title": "Second task"})

        response = client.get("/tasks?sort=-created_at")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data[0]["title"] == "Second task"

    def test_sort_by_priority(self, client):
        """Test sorting tasks by priority."""
        client.post("/tasks", json={"title": "Low", "priority": "low"})
        client.post("/tasks", json={"title": "High", "priority": "high"})
        client.post("/tasks", json={"title": "Normal", "priority": "normal"})

        response = client.get("/tasks?sort=-priority")

        assert response.status_code == status.HTTP_200_OK
        # Priority sorting is alphabetical, so high > low > normal

    def test_invalid_status_filter(self, client):
        """Test filtering by invalid status returns error."""
        response = client.get("/tasks?status=invalid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_priority_filter(self, client):
        """Test filtering by invalid priority returns error."""
        response = client.get("/tasks?priority=invalid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_pagination(self, client):
        """Test pagination with limit and offset."""
        # Create 5 tasks
        for i in range(5):
            client.post("/tasks", json={"title": f"Task {i}"})

        # Get first 2 tasks
        response = client.get("/tasks?limit=2&offset=0")
        assert len(response.json()) == 2

        # Get next 2 tasks
        response = client.get("/tasks?limit=2&offset=2")
        assert len(response.json()) == 2


class TestSubtasks:
    """Tests for subtask functionality."""

    def test_create_subtask(self, client, sample_task):
        """Test creating a subtask."""
        # Create parent task
        parent_response = client.post("/tasks", json=sample_task)
        parent_id = parent_response.json()["id"]

        # Create subtask
        response = client.post("/tasks", json={
            "title": "Subtask",
            "parent_id": parent_id
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["parent_id"] == parent_id

    def test_get_task_with_subtasks(self, client, sample_task):
        """Test getting a task includes its subtasks."""
        # Create parent task
        parent_response = client.post("/tasks", json=sample_task)
        parent_id = parent_response.json()["id"]

        # Create subtasks
        client.post("/tasks", json={"title": "Subtask 1", "parent_id": parent_id})
        client.post("/tasks", json={"title": "Subtask 2", "parent_id": parent_id})

        # Get parent task
        response = client.get(f"/tasks/{parent_id}")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["subtasks"]) == 2

    def test_delete_parent_deletes_subtasks(self, client, sample_task):
        """Test deleting a parent task also deletes subtasks."""
        # Create parent task
        parent_response = client.post("/tasks", json=sample_task)
        parent_id = parent_response.json()["id"]

        # Create subtask
        subtask_response = client.post("/tasks", json={
            "title": "Subtask",
            "parent_id": parent_id
        })
        subtask_id = subtask_response.json()["id"]

        # Delete parent
        client.delete(f"/tasks/{parent_id}")

        # Verify subtask is also deleted
        response = client.get(f"/tasks/{subtask_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_subtask_invalid_parent(self, client):
        """Test creating a subtask with invalid parent fails."""
        response = client.post("/tasks", json={
            "title": "Orphan subtask",
            "parent_id": 99999
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestBulkOperations:
    """Tests for bulk operations."""

    def test_bulk_delete(self, client):
        """Test bulk deleting tasks."""
        # Create tasks
        task1 = client.post("/tasks", json={"title": "Task 1"}).json()
        task2 = client.post("/tasks", json={"title": "Task 2"}).json()
        task3 = client.post("/tasks", json={"title": "Task 3"}).json()

        # Delete first two
        response = client.post("/tasks/bulk-delete", json={
            "ids": [task1["id"], task2["id"]]
        })

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify only task3 remains
        list_response = client.get("/tasks")
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["id"] == task3["id"]


class TestTaskStats:
    """Tests for task statistics endpoint."""

    def test_get_stats_empty(self, client):
        """Test getting stats with no tasks."""
        response = client.get("/tasks/stats/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0

    def test_get_stats_with_tasks(self, client):
        """Test getting stats with tasks."""
        # Create tasks with different statuses
        client.post("/tasks", json={"title": "Todo 1"})
        client.post("/tasks", json={"title": "Todo 2"})

        task3 = client.post("/tasks", json={"title": "Doing"}).json()
        client.put(f"/tasks/{task3['id']}", json={"status": "doing"})

        task4 = client.post("/tasks", json={"title": "Done"}).json()
        client.put(f"/tasks/{task4['id']}", json={"status": "done"})

        response = client.get("/tasks/stats/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4
        assert data["by_status"]["todo"] == 2
        assert data["by_status"]["doing"] == 1
        assert data["by_status"]["done"] == 1
