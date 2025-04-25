from dataclasses import dataclass
import datetime


@dataclass
class Chapter:
    id: int
    name: str
    water_content: int
    words: int
    symbols: int
    commonly_used_words: list[str]
    commonly_used_words_amount: list[int]
    chapters: list # по идее одлжно быть кншн list[Chapter], но так писать ошибка, решил в общем не париться тут с типизацией


@dataclass
class Diploma:
    id: int
    name: str
    author: str
    academic_supervisor: str
    year: int
    words: int
    load_date: datetime
    chapters: list[Chapter]

