"""
Module for interacting with tj. Mostly dumping tasks in tj3 file.
"""

import dataclasses
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import jaglar.ganttpro as ganttpro
from jaglar.types import Resource, Task


def normalize_name(name: str) -> str:
    """
    Standardize name string to become a valid tj id
    """

    if not name:
        return name

    name = re.sub(r"[\./\- ]", "_", name.lower())

    if name[0].isdigit():
        name = "a_" + name

    return name


def normalize_resource(resource: Resource) -> Resource:
    return dataclasses.replace(resource, name=normalize_name(resource.name))


def normalize_task(task: Task) -> Task:
    new_task = dataclasses.replace(
        task,
        name=normalize_name(task.name),
        assignee=[normalize_resource(res) for res in task.assignee],
    )

    if task.depends_on:
        new_task.depends_on = [normalize_task(t) for t in task.depends_on]

    return new_task


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

    for child in (node.children or []):
        blocks.append(format_node(child, indent + 1))

    blocks.append(indent_str + "}")

    return "\n".join(blocks)


def task_to_node(task: Task) -> Node:
    """
    Make node for given task. Note that the effort is considered in
    person-hours.
    """

    dependencies = [
        Node(type="depends", props=[dep.name]) for dep in (task.depends_on or [])
    ]

    assignees = [
        Node(type="allocate", props=[assignee.name]) for assignee in task.assignee
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
                type="limits",
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


def make_gantt_node() -> Node:
    return Node(
        type="taskreport",
        props=["\"Gantt Chart\""],
        children=[
            Node(type="formats", props=["html"]),
            Node(type="headline", props=["\"Project Gantt Chart\""]),
            Node(type="columns", props=["hierarchindex, name, start, end, effort, duration, chart"]),
            Node(type="timeformat", props=["\"%a %Y-%m-%d\""])
        ]
    )


def normalize_gantt_pro_project(project: ganttpro.Project) -> Tuple[List[Resource], List[Task]]:
    """
    Convert a ganttpro project to list of valid resources and tasks for tj.
    """

    resources = [normalize_resource(res) for res in project.resources]
    tasks = [normalize_task(task) for task in project.tasks]

    return resources, tasks


def format_project(project: Node, resources: List[Node], tasks: List[Node], generate_report=True):
    """
    Format the project in tj format. All tasks are assumed to be the lowest
    level one right now since we are mostly interesting in estimating
    timelines.
    """

    formatted_nodes = [
        format_node(project, force_brackets=True),
        *[format_node(res) for res in resources],
        *[format_node(task) for task in tasks]
    ]

    if generate_report:
        formatted_nodes.append(format_node(make_gantt_node()))

    return "\n\n".join(formatted_nodes)
