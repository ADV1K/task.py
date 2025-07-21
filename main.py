from pathlib import Path

import typer

from task_tracker import Task, TaskNotFoundError
from task_tracker.plugins.json import JsonStorage

DEFAULT_JSON_FILE = Path() / "tasks.json"

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
    with JsonStorage(DEFAULT_JSON_FILE) as tl:
        tl.list_tasks().print()


@app.command("add", short_help="Add a new task.")
def create_task(task: list[str]):
    with JsonStorage(DEFAULT_JSON_FILE) as tl:
        task_obj = Task(description=" ".join(task))
        tl.save_task(task_obj)


@app.command("done", short_help="Mark a task as completed.")
def mark_completed(task_id: str):
    with JsonStorage(DEFAULT_JSON_FILE) as tl:
        try:
            tl.mark_completed(task_id)
            print(f"Completed task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("del", short_help="Delete a task.")
def delete_task(task_id: str):
    with JsonStorage(DEFAULT_JSON_FILE) as tl:
        try:
            tl.delete_task(task_id)
            print(f"Deleted task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("clean", short_help="Remove completed tasks.")
def delete_completed(task: str, all: bool = False):
    print("UNIMPLEMENTED")


if __name__ == "__main__":
    app()
