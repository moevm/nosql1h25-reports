from dataclasses import dataclass
import datetime


class Doc:
    def __init__(self):
        self.id = None
        self.name = None
        self.author = None
        self.academic_supervisor = None # научный реководитель
        self.year = None

        # полчучить напрамую количество страниц в документе не получится
        # для этого придётся считать высоту каждой строчки текста
        # по отношению к длине и высоте страницы
        # очень муторно считать

        self.pages = None

        self.words = None
        self.load_date = None
        
        self.nominal_disclosure = None # раскрытость темы
        self.disclosure_keys = None # это должна быть запись, где будут перечислены задачи,
                                    # по которым мы потом будем считать раскрытость темы
                                    # по сути список слов, т.е. даже не предложений, а уже слов
        self.disclosure_percentage = None
        self.shingles = None

        self.structure = [] # структура всего документа - список разделов,
                            # стостоит из объектов разделов (DocSectoin)


class DocSection():
    def __init__(self):
        self.id = None
        self.name = None
        self.water_content = None
        self.words = None
        self.symbols = None

        self.commonly_used_words = None
        self.commonly_used_words_amount = None

        self.text = ''
        # таблицы и изображения договорились не читать
        # хотя на счёт таблиц не уверен, что это хорошая идея,
        # можно попробовать потом будет как-то учесть их
        
        self.upper = None
        self.level = None
        
        self.structure = [] # если есть какие-то подразделы - то тут будет список
                            # с ними, по сути список объектов разделов (DocSectoin)


@dataclass
class Diploma:
    name: str
    author: str
    academic_supervisor: str
    year: int
    pages: int
    words: int
    nominal_disclosure: int
    load_date: datetime
    disclosure_keys: list[str]
    disclosure_percentage: list[int]
    shingles: list[int]


@dataclass
class Chapter:
    name: str
    water_content: int
    words: int
    symbols: int
    commonly_used_words: list[str]
    commonly_used_words_amount: list[int]


def doc_section_to_dict(doc_section: DocSection) -> dict:
    doc_section_dict = doc_section.__dict__.copy()
    doc_section_dict.pop('upper', None)
    doc_section_dict['structure'] = []
    for e in doc_section.structure:
        doc_section_dict['structure'].append(doc_section_to_dict(e))
    return doc_section_dict

def doc_section_to_dataclass(doc_section: DocSection) -> Chapter:
    return Chapter(
        name=doc_section.name,
        water_content=doc_section.water_content,
        words=doc_section.words,
        symbols=doc_section.symbols,
        commonly_used_words=doc_section.commonly_used_words,
        commonly_used_words_amount=doc_section.commonly_used_words_amount
    )

def doc_to_dict(doc: Doc) -> dict:
    doc_dict = doc.__dict__.copy()
    doc_dict['structure'] = []
    for e in doc.structure:
        doc_dict['structure'].append(doc_section_to_dict(e))
    return doc_dict

def doc_to_dataclass(doc: Doc) -> Diploma:
    return Diploma(
        name=doc.name,
        author=doc.author,
        academic_supervisor=doc.academic_supervisor,
        year=doc.year,
        pages=doc.pages,
        words=doc.words,
        nominal_disclosure=doc.nominal_disclosure,
        load_date=doc.load_date,
        disclosure_keys=doc.disclosure_keys,
        disclosure_percentage=doc.disclosure_percentage,
        shingles=doc.shingles,
    )
