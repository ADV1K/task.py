from datetime import datetime
from enum import StrEnum, auto
from typing import Optional

from pydantic import BaseModel, Field
from rich.box import MINIMAL
from rich.console import Console
from rich.table import Table
from rich.text import Text


class ProgressStatus(StrEnum):
    TODO = auto()
    ACTIVE = auto()
    DONE = auto()


class Task(BaseModel):
    description: str
    status: ProgressStatus = ProgressStatus.TODO
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    description: Optional[str]
    status: Optional[ProgressStatus]
    created_at: Optional[datetime]
    due_date: Optional[datetime]


class TaskList(BaseModel):
    tasks: dict[str, Task] = Field(default_factory=dict)

    def print(self):
        display_task_list(self)


def display_task_list(task_list: TaskList) -> None:
    """
    Displays a rich table representation of the TaskList.
    """
    console = Console()
    if not task_list.tasks:
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

    for task_id, task in task_list.tasks.items():
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


class Base(Exception):
    pass


class StorageError(Base):
    pass


class TaskNotFoundError(Base):
    pass


class TaskUpdateError(Base):
    pass
