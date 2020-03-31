"""
Module for working with ganttpro exported data.
"""

from typing import Dict, List
from xml.etree.ElementTree import fromstring

import pandas as pd
from pydash import py_
from xmljson import badgerfish as bf

from jaglar.types import Resource, Task
from jaglar.utils import map_keys


def read_xlsx_export(file_path: str):
    return pd.read_excel(file_path, header=3)


def read_xml_export(file_path: str):
    with open(file_path) as fp:
        data = bf.data(fromstring(fp.read()))

    def _clean_key(k: str) -> str:
        try:
            return k.split("}", 1)[1]
        except IndexError:
            return k

    return map_keys(data, _clean_key)


class Project:
    """
    A gantt pro project. This needs both the excel and xml export because both
    have different data formats.
    """

    def __init__(self, xlsx_path: str, xml_path: str):
        self.xlsx_data = read_xlsx_export(xlsx_path)
        self.xml_data = read_xml_export(xml_path)

    @property
    def resources(self) -> List[Resource]:
        """
        Parse list of resources using excel data.
        """

        assignments = [
            it.split(",")
            for it in self.xlsx_data["Assigned to"].dropna().tolist()
        ]
        return [Resource(name=name.strip()) for name in py_.uniq(py_.flatten(assignments))]

    @property
    def tasks(self):
        """
        Return tasks with dependencies and resources assigned. This merges
        information from both sources. Also we only consider tasks with type
        task and not groups.
        """

        resources = self.resources

        # NOTE: We use WBS Number for identifying tasks
        excel_info: Dict[str, Task] = {}

        for _, row in self.xlsx_data.iterrows():
            if row["Type"] != "task":
                continue

            try:
                assignees = [Resource(name=name.strip()) for name in row["Assigned to"].split(",")]
            except AttributeError:
                # There are cases where resources are not assigned
                assignees = [Resource(name="Ghost")]

            excel_info[row["WBS Number"]] = Task(
                name=row["Task name / Title"],
                assignee=assignees,
                effort=int(row["Duration (hours)"])
            )

        return list(excel_info.values())
