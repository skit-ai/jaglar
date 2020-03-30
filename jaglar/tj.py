"""
Module for interacting with tj. Mostly dumping tasks in tj3 file.
"""

from typing import List, Optional

from jaglar.types import Resource, Task


@dataclass
class Snippet:
    """
    A snippet is a piece that maps to a valid taskjuggler code block. This
    doesn't cover macros.
    """

    type: str
    props: List[str]
    children: Optional[List["Snippet"]] = None


def format_snippet(snippet: Snippet, indent=0, force_brackets=False) -> str:
    """
    Convert snippet to str that goes in a tj file.
    """

    indent_str = "  " * indent
    top_str = indent_str + snippet.type + " " + " ".join(snippet.props)

    if not force_brackets:
        if not snippet.children:
            return top_str

    blocks = [top_str + " {"]

    for child in snippet.children:
        blocks.append(format_snippet(child, indent + 1))

    blocks.append("}")

    return "\n".join(blocks)



def resource_to_snippet(resource: Resource) -> Snippet:
    """
    Convert a resource to tj snippet.
    """

    return Snippet(
        type="resource",
        props=[resource.name, f"\"{resource.name}\""],
        children=[
            Snippet(
                type="limit",
                props=[],
                children=[Snippet(type="dailymax", props=[f"{resource.hours_per_day}h"])]
            )
        ]
    )


def make_project_snippet(project_id: str, project_name: str,
                         start_date: str, end_date: str) -> Snippet:
    """
    Make tj project in a snippet format. `end_date` can be in the diff format.
    """

    return Snippet(
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
