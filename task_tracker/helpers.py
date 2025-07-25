import re
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Iterable

import dateparser
import humanize
from rich.console import Console
from rich.table import Table
from rich.text import Text

from task_tracker import ProgressStatus, Task, TaskID

TAGS_PATTERN = re.compile(r"^@(?P<tag_name>\S+)$")  # Matches @tag
DUE_DATE_PATTERN = re.compile(r"^due:(?P<due_value>\S+)$")  # Matches due:value


def print_error(error: str):
    Console().print(f"[italic red]{error: str}[/]")


@contextmanager
def Timer(label):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"{label} took {end - start:.4f} seconds")


def task_parser(words: list[str]) -> Task:
    task = Task()
    desc_parts = []

    for word in words:
        m_tag = TAGS_PATTERN.fullmatch(word)
        m_due = DUE_DATE_PATTERN.fullmatch(word)

        if m_tag:
            task.tags.add(m_tag.group("tag_name"))
        elif m_due:
            due_date = dateparser.parse(
                m_due.group("due_value"), settings={"PREFER_DATES_FROM": "future"}
            )
            if due_date:
                task.due_date = due_date
        else:
            desc_parts.append(word.strip())

    task.description = " ".join(desc_parts)
    return task


def print_tasks(tasks: Iterable[tuple[TaskID, Task]]) -> None:
    """
    Displays a rich table representation of the TaskList.
    """
    console = Console()
    if not tasks:
        print_error("No tasks found. Add a task using `task add`")
        return

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
    table.add_column("[#FFC300]Tags[/]", justify="center", style="green")

    for task_id, task in tasks:
        status_style = {
            ProgressStatus.TODO: "bold yellow",
            ProgressStatus.ACTIVE: "bold blue",
            ProgressStatus.DONE: "bold green",
        }.get(task.status, "white")

        table.add_row(
            task_id,
            task.description,
            Text(task.status.value, style=status_style),
            humanize.naturalday(task.created_at),
            humanize.naturalday(task.due_date) if task.due_date else "N/A",
            ", ".join(task.tags),
        )

    console.print(table)


def sort_by_due_date(tasks: dict[TaskID, Task]) -> Iterable[tuple[TaskID, Task]]:
    """Sorts a dictionary of tasks by their due_date. Tasks with a None due_date will always appear at the end."""
    return sorted(
        tasks.items(),
        key=lambda item: (
            item[1].due_date is None,  # True (1) for None, False (0) for actual dates
            item[1].due_date
            if item[1].due_date is not None
            else datetime.max,  # Actual date or largest possible datetime
        ),
    )
