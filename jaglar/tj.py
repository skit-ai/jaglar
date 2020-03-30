"""
Module for interacting with tj. Mostly dumping tasks in tj3 file.
"""

from typing import List, Optional

from jaglar.types import Resource, Task


@dataclass
class Node:
    """
    A node is a piece that maps to a valid taskjuggler code block. This
    doesn't cover macros.
    """

    type: str
    props: List[str]
    children: Optional[List["Node"]] = None


def format_node(node: Node, indent=0, force_brackets=False) -> str:
    """
    Convert node to str that goes in a tj file.
    """

    indent_str = "  " * indent
    top_str = indent_str + node.type + " " + " ".join(node.props)

    if not force_brackets:
        if not node.children:
            return top_str

    blocks = [top_str + " {"]

    for child in node.children:
        blocks.append(format_node(child, indent + 1))

    blocks.append("}")

    return "\n".join(blocks)


def task_to_node(task: Task) -> Node:
    """
    Make node for given task. Note that the effort is considered in
    person-hours.
    """

    dependencies = [
        Node(type="depends", props=[dep.name]) for dep in task.depends_on
    ]

    assignees = [
        Node(type="allocate", props=[assignee]) for assignee in task.assignee
    ]

    return Node(
        type="task",
        props=[task.name, f"\"{task.name}\""],
        children=[
            Node(
                type="effort",
                props=[f"{task.effort}h"]
            ),
            *assignees, *dependencies
        ]
    )


def resource_to_node(resource: Resource) -> Node:
    """
    Convert a resource to tj node.
    """

    return Node(
        type="resource",
        props=[resource.name, f"\"{resource.name}\""],
        children=[
            Node(
                type="limit",
                props=[],
                children=[Node(type="dailymax", props=[f"{resource.hours_per_day}h"])]
            )
        ]
    )


def make_project_node(project_id: str, project_name: str,
                      start_date: str, end_date: str) -> Node:
    """
    Make tj project in a node format. `end_date` can be in the diff format.
    """

    return Node(
        type="project",
        props=[project_id, f"\"{project_name}\"", start_date, end_date]
    )


def write_to_tj_file(tasks: List[Task], resources: List[Resource], file_path: str):
    """
    Write given tasks to given file in tj format. All tasks are assumed to be
    the lowest level one right now since we are mostly interesting in
    estimating timelines.
    """

    raise NotImplementedError()
