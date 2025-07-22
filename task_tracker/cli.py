from dataclasses import dataclass
from pathlib import Path

import typer

from task_tracker import (
    ProgressStatus,
    StorageError,
    TaskNotFoundError,
    TaskUpdate,
)
from task_tracker.helpers import print_tasks, sort_by_due_date, task_parser
from task_tracker.plugins.json import JsonStorage, TaskStorageProtocol

DEFAULT_JSON_FILE = Path().home() / "tasks.json"
app = typer.Typer(no_args_is_help=True)


@dataclass
class AppContext:
    store: TaskStorageProtocol


@app.callback()
def main(ctx: typer.Context):
    """Manage your tasks. Anytime. Anywhere."""
    try:
        ctx.obj = AppContext(store=JsonStorage(DEFAULT_JSON_FILE))
    except StorageError:
        print("Error: Invalid task data file. Please check 'tasks.json'.")
        raise typer.Exit(1)


@app.command("list")
@app.command("ls", hidden=True)
def list_tasks(ctx: typer.Context):
    """List all tasks. Alias: ls"""
    with ctx.obj.store as store:
        print_tasks(sort_by_due_date(store.list_tasks()))


@app.command("add")
def create_task(task: list[str], ctx: typer.Context):
    """Add a new task."""
    with ctx.obj.store as store:
        store.create_task(task_parser(task))


@app.command("done")
def mark_completed(task_id: str, ctx: typer.Context):
    """Mark a task is completed."""
    with ctx.obj.store as store:
        try:
            task = store.read_task(task_id)
            task.status = ProgressStatus.DONE
            store.update_task(task_id, TaskUpdate.model_validate(task))
            print(f"Task #{task_id} marked as done.")
        except TaskNotFoundError:
            print("No task found.")


@app.command("active")
def mark_active(task_id: str, ctx: typer.Context):
    """Mark a task is active."""
    with ctx.obj.store as store:
        try:
            task = store.read_task(task_id)
            task.status = ProgressStatus.ACTIVE
            store.update_task(task_id, TaskUpdate.model_validate(task))
            print(f"Working on Task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("del")
def delete_task(task_id: str, ctx: typer.Context):
    """Delete a task."""
    with ctx.obj.store as store:
        try:
            store.delete_task(task_id)
            print(f"Deleted task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("clean")
def delete_completed(ctx: typer.Context):
    """Remove completed tasks."""
    with ctx.obj.store as store:
        count = 0
        for task_id, task in store.list_tasks().items():
            if store.read_task(task_id).status == ProgressStatus.DONE:
                count += 1
                store.delete_task(task_id)
        print(f"Deleted {count} completed tasks.")


if __name__ == "__main__":
    app()
