"""
Module for working with ganttpro exported data.
"""


from xml.etree.ElementTree import fromstring

import pandas as pd
from pydash import py_
from xmljson import badgerfish as bf

from jaglar.types import Resource


def read_xlsx_export(file_path: str):
    return pd.read_excel(file_path, header=3)


def read_xml_export(file_path: str):
    with open(file_path) as fp:
        return bf.data(fromstring(fp.read()))


class Project:
    """
    A gantt pro project. This needs both the excel and xml export because both
    have different data formats.
    """

    def __init__(self, xlsx_path: str, xml_path: str):
        self.xlsx_data = read_xlsx_export(xlsx_path)
        self.xml_data = read_xml_export(xml_path)

    @property
    def resources(self):
        assignments = [
            it.split(",")
            for it in self.xlsx_data["Assigned to"].dropna().tolist()
        ]
        return [Resource(name=name.strip()) for name in py_.uniq(py_.flatten(assignments))]

    @property
    def tasks(self):
        raise NotImplementedError()
