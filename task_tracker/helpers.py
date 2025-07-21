from rich.console import Console
from rich.table import Table
from rich.text import Text

from task_tracker import ProgressStatus, Task, TaskID


def print_tasks(tasks: dict[TaskID, Task]) -> None:
    """
    Displays a rich table representation of the TaskList.
    """
    console = Console()
    if not tasks:
        console.print(Text("No tasks found.", justify="center", style="italic red"))

    table = Table(
        # title="[bold blue]Task List[/bold blue]",
        show_header=True,
        header_style="bold green",
    )
    table.add_column("[#DAF7A6]ID[/]", style="dim", justify="left")
    table.add_column("[#FFC300]Description[/]", style="cyan", justify="left")
    table.add_column("[#DAF7A6]Status[/]", justify="center")
    table.add_column("[#FFC300]Created At[/]", justify="center", style="dim")
    table.add_column("[#DAF7A6]Due Date[/]", justify="center", style="magenta")

    for task_id, task in tasks.items():
        created_at_str = task.created_at.strftime("%Y-%m-%d %H:%M")
        due_date_str = (
            task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else "N/A"
        )
        status_style = {
            ProgressStatus.TODO: "bold yellow",
            ProgressStatus.ACTIVE: "bold blue",
            ProgressStatus.DONE: "bold green",
        }.get(task.status, "white")

        table.add_row(
            str(task_id),
            task.description,
            Text(task.status.value, style=status_style),
            created_at_str,
            due_date_str,
        )

    console.print(table)
