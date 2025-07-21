import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel, Field, ValidationError

from task_tracker import (
    ProgressStatus,
    StorageError,
    Task,
    TaskID,
    TaskNotFoundError,
    TaskUpdate,
    TaskUpdateError,
)
from task_tracker.plugins import TaskStorageProtocol


class TaskJsonFile(BaseModel):
    """tasks.json file format"""
    tasks: dict[TaskID, Task] = Field(default_factory=dict)


class JsonStorage(TaskStorageProtocol):
    def __init__(self, filename: Path) -> None:
        """Load the task file in memory"""
        self.filename = filename
        if not self.filename.exists() or self.filename.stat().st_size == 0:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            self.filename.write_text(TaskJsonFile().model_dump_json(indent=4))

        try:
            self._file = TaskJsonFile.model_validate_json(self.filename.read_bytes())
            self._tasks = self._file.tasks
        except (json.JSONDecodeError, ValidationError) as e:
            raise StorageError(
                f"Corrupt or invalid json in {self.filename}: {e}"
            ) from e

    def _generate_new_id(self) -> TaskID:
        """Returns Biggest key + 1"""
        return str(int(max(self._tasks.keys() or [0])) + 1)

    def list_tasks(self) -> dict[TaskID, Task]:
        return deepcopy(self._tasks)

    def create_task(self, task: Task) -> None:
        self._tasks[self._generate_new_id()] = task

    def read_task(self, task_id: TaskID) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError
        return task

    def update_task(self, task_id: TaskID, updates: TaskUpdate) -> None:
        current_task = self._tasks.get(task_id)
        if not current_task:
            raise TaskNotFoundError

        try:
            updated_task = current_task.model_copy(
                update=updates.model_dump(exclude_none=True)
            )
            self._tasks[task_id] = updated_task
        except ValidationError as e:
            raise TaskUpdateError(
                f"Unable to update task with id {task_id}: {e}"
            ) from e

    def delete_task(self, task_id: TaskID) -> None:
        try:
            self._tasks.pop(task_id)
        except KeyError:
            raise TaskNotFoundError

    def close(self) -> None:
        self.filename.write_text(self._file.model_dump_json(indent=4))

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
