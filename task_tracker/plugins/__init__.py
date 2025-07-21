from typing import Any, Protocol, Self, runtime_checkable

from task_tracker import Task, TaskID, TaskUpdate


@runtime_checkable
class TaskStorageProtocol(Protocol):
    def list_tasks(self) -> dict[TaskID, Task]:
        """List all the tasks"""
        ...

    def create_task(self, task: Task) -> None:
        """Create the task with a unique task_id"""
        ...

    def read_task(self, task_id: str) -> Task:
        """
        Read the Task model for the given task_id

        raises TaskNotFoundError if task_id is not present
        """
        ...

    def update_task(self, task_id: str, updates: TaskUpdate) -> None:
        """
        Update the given task_id

        raises TaskNotFoundError if task_id is not present
        raises TaskUpdateError if the update models is malformed
        """
        ...

    def delete_task(self, task_id: str) -> None:
        """
        Delete the given task_id

        raises TaskNotFoundError if task_id is not present
        """
        ...

    def close(self) -> None:
        """Close the storage container or network connection"""
        ...

    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
