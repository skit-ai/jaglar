from typing import List, Optional


@dataclass
class Resource:
    name: str
    hours_per_day: int = 8


@dataclass
class Task:
    name: str
    assignee: List[Resource]
    effort: float
    depends_on: Optional[List["Task"]] = None
