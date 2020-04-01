"""
Basic example showing how to generate a tjp file programmatically.

Usage:
  simple.py <output-file>
"""

from docopt import docopt

from jaglar.tj import (format_project, make_project_node, resource_to_node,
                       task_to_node)
from jaglar.types import Resource, Task

pj = make_project_node("pj", "pj", "2020-03-30", "+2m")

resources = [
    Resource(name="ml"),
    Resource(name="product"),
    Resource(name="annotator"),
    Resource(name="eng")
]

t1 = Task(name="t1", assignee=[Resource(name="annotator")], effort=20)
t2 = Task(name="t2", assignee=[Resource(name="ml")], effort=8, depends_on=[t1])
t3 = Task(name="t3", assignee=[Resource(name="ml")], effort=8, depends_on=[t2])

if __name__ == "__main__":
    args = docopt(__doc__)

    with open(args["<output-file>"], "w") as fp:
        task_nodes = [task_to_node(t) for t in [t1, t2, t3]]
        resource_nodes = [resource_to_node(r) for r in resources]

        fp.write(format_project(pj, resource_nodes, task_nodes))
