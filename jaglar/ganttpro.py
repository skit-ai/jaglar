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
                name=row["Task name / Title"] + " " + row["WBS Number"],
                assignee=assignees,
                effort=int(row["Duration (hours)"])
            )

        # NOTE: There are a few assumptions here about number of projects and
        #       all. This is not foolproof.

        # These tasks are the superset of what we are interested in excel_info
        xml_tasks = self.xml_data["Project"]["Tasks"]["Task"]

        def _sanitize_wbs(wbs: str) -> str:
            wbs = str(wbs)
            # HACK: xml data has extra thing added in WBS
            if "." in wbs:
                return wbs.split(".", 1)[1]
            else:
                return wbs

        uid_to_wbs = {t["UID"]["$"]: _sanitize_wbs(t["WBS"]["$"]) for t in xml_tasks}

        # Mostly mapping from WBS to list of dependencies, also specified in WBS
        xml_info: Dict[str, List[str]] = {}

        for xml_task in xml_tasks:
            wbs = _sanitize_wbs(xml_task["WBS"]["$"])

            if "PredecessorLink" in xml_task:
                pred_link = xml_task["PredecessorLink"]

                if isinstance(pred_link, dict):
                    predecessor_wbses = [uid_to_wbs[pred_link["PredecessorUID"]["$"]]]
                elif isinstance(pred_link, list):
                    predecessor_wbses = [
                        uid_to_wbs[it["PredecessorUID"]["$"]]
                        for it in pred_link
                    ]
                else:
                    raise TypeError(f"Wrong type of PredecessorLink")
                xml_info[wbs] = predecessor_wbses

        # Now we patch the excel_info tasks with dependency information
        for wbs, predecessor_wbses in xml_info.items():
            if wbs not in excel_info:
                continue

            excel_info[wbs].depends_on = [excel_info[p_wbs] for p_wbs in predecessor_wbses]

        return list(excel_info.values())
