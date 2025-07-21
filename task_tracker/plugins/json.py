import json
from pathlib import Path
from typing import Any, Optional, Self

from pydantic import ValidationError

from task_tracker import (
    ProgressStatus,
    StorageError,
    Task,
    TaskList,
    TaskNotFoundError,
    TaskUpdate,
    TaskUpdateError,
)
from task_tracker.plugins import TaskStorageProtocol


class JsonStorage(TaskStorageProtocol):
    def __init__(self, filename: Path) -> None:
        """Open file and load tasklist in memory"""
        self.filename = filename
        if not self.filename.exists() or self.filename.stat().st_size == 0:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            self.filename.write_text(TaskList().model_dump_json(indent=4))

        try:
            self._task_list = TaskList.model_validate_json(self.filename.read_bytes())
            self._tasks = self._task_list.tasks
        except (json.JSONDecodeError, ValidationError) as e:
            raise StorageError(
                f"Corrupt or invalid data in {self.filename}: {e}"
            ) from e

    def _generate_new_id(self) -> str:
        """Returns Biggest key + 1"""
        return str(int(max(self._tasks.keys() or [0])) + 1)

    def list_tasks(self) -> TaskList:
        return self._task_list

    def load_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def save_task(self, task: Task) -> None:
        self._tasks[self._generate_new_id()] = task

    def mark_completed(self, task_id: str) -> None:
        task = self._tasks.get(task_id)
        if not task:
            raise TaskNotFoundError

        task.status = ProgressStatus.DONE

    def delete_task(self, task_id: str) -> None:
        try:
            self._tasks.pop(task_id)
        except KeyError:
            raise TaskNotFoundError

    def update_task(self, task_id: str, updates: TaskUpdate) -> None:
        current_task = self._tasks.get(task_id)
        if not current_task:
            raise TaskNotFoundError

        try:
            updated_task = current_task.model_copy(
                update=updates.model_dump(exclude_none=True)
            )
            self._task_list.tasks[task_id] = updated_task
        except ValidationError as e:
            raise TaskUpdateError(
                f"Unable to update task with id {task_id}: {e}"
            ) from e

    def cleanup(self) -> None:
        """Write file to disk"""
        self.filename.write_text(self._task_list.model_dump_json(indent=4))

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.cleanup()
