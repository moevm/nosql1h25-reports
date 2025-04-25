import datetime
from dataclasses import dataclass


@dataclass
class Chapter:
    id: int | None
    id_diploma: int | None
    name: str
    water_content: int
    words: int
    symbols: int
    commonly_used_words: list[str]
    commonly_used_words_amount: list[int]
    chapters: list['Chapter']


@dataclass
class Diploma:
    id: int | None
    name: str
    author: str
    academic_supervisor: str | None  # None, если не получилось извлечь руководителя
    year: int
    words: int
    load_date: datetime
    chapters: list[Chapter]
