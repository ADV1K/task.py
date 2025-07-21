from dataclasses import dataclass
from pathlib import Path

import typer

from task_tracker import (
    ProgressStatus,
    StorageError,
    Task,
    TaskNotFoundError,
    TaskUpdate,
)
from task_tracker.helpers import print_tasks, sort_by_due_date, task_parser
from task_tracker.plugins.json import JsonStorage, TaskStorageProtocol

DEFAULT_JSON_FILE = Path() / "tasks.json"
app = typer.Typer()


@dataclass
class AppContext:
    store: TaskStorageProtocol


@app.callback()
def main(ctx: typer.Context):
    """
    Manage your tasks. Anytime. Anywhere.
    """
    try:
        ctx.obj = AppContext(store=JsonStorage(DEFAULT_JSON_FILE))
    except StorageError:
        print("Error: Invalid task data file. Please check 'tasks.json'.")
        raise typer.Exit(1)


@app.command("list", short_help="List all tasks. Alias: ls")
@app.command("ls", hidden=True)
def list_tasks(ctx: typer.Context):
    with ctx.obj.store as store:
        print_tasks(sort_by_due_date(store.list_tasks()))


@app.command("add", short_help="Add a new task.")
def create_task(task: list[str], ctx: typer.Context):
    with ctx.obj.store as store:
        store.create_task(task_parser(task))


@app.command("done", short_help="Mark a task as completed.")
def mark_completed(task_id: str, ctx: typer.Context):
    with ctx.obj.store as store:
        try:
            task = store.read_task(task_id)
            task.status = ProgressStatus.DONE
            store.update_task(task_id, TaskUpdate.model_validate(task))
            print(f"Task #{task_id} marked as done.")
        except TaskNotFoundError:
            print("No task found.")


@app.command("del", short_help="Delete a task.")
def delete_task(task_id: str, ctx: typer.Context):
    with ctx.obj.store as store:
        try:
            store.delete_task(task_id)
            print(f"Deleted task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("clean", short_help="Remove completed tasks.")
def delete_completed(ctx: typer.Context):
    with ctx.obj.store as store:
        count = 0
        for task_id, task in store.list_tasks().items():
            if store.read_task(task_id).status == ProgressStatus.DONE:
                count += 1
                store.delete_task(task_id)
        print(f"Deleted {count} completed tasks.")


if __name__ == "__main__":
    app()
