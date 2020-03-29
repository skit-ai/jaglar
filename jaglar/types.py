from typing import List


@dataclass
class Task:
    name: str
    assignee: str
    time: float
    depends_on: List["Task"]
