import datetime
from dataclasses import dataclass
from typing import Tuple


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
    academic_supervisor: str
    year: int
    words: int
    pages: int
    minimal_disclosure: int
    load_date: datetime
    disclosure_keys: list[str]
    disclosure_percentage: list[int]
    chapters: list['Chapter']
    shingles: list[int] | None = None
    similar_diplomas: list[Tuple[int, str, int]] | None = None
