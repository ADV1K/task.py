import typer

from task_tracker import ProgressStatus, TaskNotFoundError, TaskUpdate
from task_tracker.config import context
from task_tracker.helpers import Timer, print_tasks, sort_by_due_date, task_parser
from task_tracker.plugins import AvailablePlugins

# from task_tracker.plugins.google import google_plugin_cli

# PLUGINS
plugin = typer.Typer()
# plugin.add_typer(google_plugin_cli, name="google", help="Manage Google Tasks Plugin")

app = typer.Typer(no_args_is_help=True)
app.add_typer(plugin, name="plugin", help="Manage Plugins")


@app.callback()
def setup():
    """Manage your tasks. Anytime. Anywhere."""


# ROOT COMMANDS
@app.command("ls")
def list_tasks():
    """List all tasks."""
    with context.store as store:
        print_tasks(sort_by_due_date(store.list_tasks()))


@app.command("add")
def create_task(task: list[str]):
    """Add a new task."""
    with context.store as store:
        store.create_task(task_parser(task))


@app.command("done")
def mark_completed(task_id: str):
    """Mark a task is completed."""
    with context.store as store:
        try:
            task = store.read_task(task_id)
            task.status = ProgressStatus.DONE
            store.update_task(task_id, TaskUpdate.model_validate(task))
            print(f"Task #{task_id} marked as done.")
        except TaskNotFoundError:
            print("No task found.")


@app.command("active")
def mark_active(task_id: str):
    """Mark a task is active."""
    with context.store as store:
        try:
            task = store.read_task(task_id)
            task.status = ProgressStatus.ACTIVE
            store.update_task(task_id, TaskUpdate.model_validate(task))
            print(f"Working on Task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("del")
def delete_task(task_id: str):
    """Delete a task."""
    with context.store as store:
        try:
            store.delete_task(task_id)
            print(f"Deleted task #{task_id}")
        except TaskNotFoundError:
            print("No task found.")


@app.command("clean")
def delete_completed():
    """Remove completed tasks."""
    with context.store as store:
        count = 0
        for task_id, task in store.list_tasks().items():
            if store.read_task(task_id).status == ProgressStatus.DONE:
                count += 1
                store.delete_task(task_id)
        print(f"Deleted {count} completed tasks.")


# PLUGIN COMMANDS
@plugin.command("use")
def change_default_plugin(plugin: AvailablePlugins):
    """Switch default Plugin"""
    print("DONE")
