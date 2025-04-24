from dataclasses import dataclass
import datetime


@dataclass
class Chapter:
    name: str
    water_content: int
    words: int
    symbols: int
    commonly_used_words: list[str]
    commonly_used_words_amount: list[int]
    chapters: list # по идее одлжно быть кншн list[Chapters], но так писать ошибка, решил в общем не париться тут с типизацией


@dataclass
class Diploma:
    name: str
    author: str
    academic_supervisor: str
    year: int
    pages: int
    words: int
    minimal_disclosure: int
    load_date: datetime
    disclosure_keys: list[str]
    disclosure_percentage: list[int]
    shingles: list[int]
    chapters: list[Chapter]

