from pathlib import Path

import typer

from task_tracker import ProgressStatus, Task, TaskNotFoundError, TaskUpdate
from task_tracker.helpers import print_tasks
from task_tracker.plugins.json import JsonStorage

DEFAULT_JSON_FILE = Path() / "tasks.json"
Tasks = JsonStorage(DEFAULT_JSON_FILE)

app = typer.Typer()


@app.callback()
def main():
    """
    Manage your tasks. Anytime. Anywhere.
    """
    pass


@app.command("list", short_help="List all tasks. Alias: ls")
@app.command("ls", hidden=True)
def list_tasks():
    with Tasks as t:
        print_tasks(t.list_tasks())


@app.command("add", short_help="Add a new task.")
def create_task(task: list[str]):
    with Tasks as t:
        task_obj = Task(description=" ".join(task))
        t.create_task(task_obj)


@app.command("done", short_help="Mark a task as completed.")
def mark_completed(task_id: str):
    with Tasks as t:
        try:
            task = t.read_task(task_id)
            task.status = ProgressStatus.DONE
            t.update_task(task_id, TaskUpdate.model_validate(task))
            print(f"Task #{task_id} marked as done.")
        except TaskNotFoundError:
            print("No task found.")


@app.command("del", short_help="Delete a task.")
def delete_task(task_id: str):
    with Tasks as t:
        try:
            t.delete_task(task_id)
            print(f"Deleted task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("clean", short_help="Remove completed tasks.")
def delete_completed():
    with Tasks as t:
        count = 0
        for task_id, task in t.list_tasks().items():
            if t.read_task(task_id).status == ProgressStatus.DONE:
                count += 1
                t.delete_task(task_id)
        print(f"Deleted {count} completed tasks.")


if __name__ == "__main__":
    app()
