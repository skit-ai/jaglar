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
    children: Optional["Snippet"] = None


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


def write_to_tj_file(tasks: List[Task], resources: List[Resource], file_path: str):
    """
    Write given tasks to given file in tj format.
    """

    raise NotImplementedError()
