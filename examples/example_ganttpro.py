"""
Usage:
  example.py <output-file>
"""

from docopt import docopt

from jaglar.ganttpro import Project
from jaglar.tj import (format_project, make_project_node,
                       normalize_gantt_pro_projects, resource_to_node,
                       task_to_node)

gpjs = [
    # Project("c1", "./data/v4_ On-cloud-1-language.xlsx", "./data/v4_ On-cloud-1-language.xml"),
    # Project("c2", "./data/v4_ On-cloud-2-language.xlsx", "./data/v4_ On-cloud-2-language.xml"),
    # Project("p1", "./data/v4_ On-premise-1-language.xlsx", "./data/v4_ On-premise-1-language.xml"),
    # Project("p3", "./data/v4_ On-premise-2-language.xlsx", "./data/v4_ On-premise-2-language.xml")
]

pj = make_project_node("pj", "pj", "2020-04-01", "+40m")

resources, tasks = normalize_gantt_pro_projects(*gpjs)

if __name__ == "__main__":
    args = docopt(__doc__)

    with open(args["<output-file>"], "w") as fp:
        task_nodes = [task_to_node(t) for t in tasks]
        resource_nodes = [resource_to_node(r) for r in resources]

        fp.write(format_project(pj, resource_nodes, task_nodes))
