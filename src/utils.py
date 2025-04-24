import json
from datetime import datetime

from src.parsing_docx.docClasses import (
    Doc,
    DocSection,
)

from src.data_types import (
    Chapter,
    Diploma
)


# serialize/deserialize Chapter
def chapter_to_dict(chapter: Chapter) -> dict:
    chapter_dict = chapter.__dict__.copy()
    chapter_dict['chapters'] = []
    for e in chapter.chapters:
        chapter_dict['chapters'].append(chapter_to_dict(e))
    return chapter_dict

def chapter_from_dict(chapter: dict) -> Chapter:
    name = chapter['name']
    water_content = chapter['water_content']
    words = chapter['words']
    symbols = chapter['symbols']
    commonly_used_words = chapter['commonly_used_words']
    commonly_used_words_amount = chapter['commonly_used_words_amount']
    chapters = []
    for e in chapter['chapters']:
        chapters.append(chapter_from_dict(e))
    return Chapter(
        name=name,
        water_content=water_content,
        words=words,
        symbols=symbols,
        commonly_used_words=commonly_used_words,
        commonly_used_words_amount=commonly_used_words_amount,
        chapters=chapters
    )

# serialize/deserialize Diploma
def diploma_to_dict(diploma: Diploma) -> dict:
    diploma_dict = diploma.__dict__.copy()
    if isinstance(diploma_dict['load_date'], datetime):
        diploma_dict['load_date'] = diploma_dict['load_date'].isoformat()
    diploma_dict['chapters'] = []
    for e in diploma.chapters:
        diploma_dict['chapters'].append(chapter_to_dict(e))
    return diploma_dict

def diploma_from_dict(diploma: dict) -> Diploma:
    name = diploma['name']
    author = diploma['author']
    academic_supervisor = diploma['academic_supervisor']
    year = diploma['year']
    pages = diploma['pages']
    words = diploma['words']
    minimal_disclosure = diploma['minimal_disclosure']
    if diploma.get('load_date') and diploma['load_date']:
        load_date = datetime.fromisoformat(diploma['load_date'])
    else:
        load_date = diploma['load_date']
    disclosure_keys = diploma['disclosure_keys']
    disclosure_percentage = diploma['disclosure_percentage']
    shingles = diploma['shingles']
    chapters = []
    for e in diploma['chapters']:
        chapters.append(chapter_from_dict(e))
    return Diploma(
        name=name,
        author=author,
        academic_supervisor=academic_supervisor,
        year=year,
        pages=pages,
        words=words,
        minimal_disclosure=minimal_disclosure,
        load_date=load_date,
        disclosure_keys=disclosure_keys,
        disclosure_percentage=disclosure_percentage,
        shingles=shingles,
        chapters=chapters
    )

# serialize/deserialize DocSection
def doc_section_to_dict(doc_section: DocSection) -> dict:
    doc_section_dict = doc_section.__dict__.copy()
    doc_section_dict.pop('upper', None)
    doc_section_dict['structure'] = []
    for e in doc_section.structure:
        doc_section_dict['structure'].append(doc_section_to_dict(e))
    return doc_section_dict

def doc_section_from_dict(doc_section: dict) -> DocSection:
    name = doc_section['name']
    text = doc_section['text']
    upper = None
    level = doc_section['level']
    structure = []
    for e in doc_section['structure']:
        structure.append(doc_section_from_dict(e))
    return DocSection(
        name=name,
        text=text,
        upper=upper,
        level=level,
        structure=structure
    )

# serialize/deserialize Doc
def doc_to_dict(doc: Doc) -> dict:
    doc_dict = doc.__dict__.copy()
    doc_dict['structure'] = []
    for e in doc.structure:
        doc_dict['structure'].append(doc_section_to_dict(e))
    return doc_dict

def doc_from_dict(doc: dict) -> Doc:
    name = doc['name']
    author = doc['author']
    academic_supervisor = doc['academic_supervisor']
    year = doc['year']
    structure = []
    for e in doc['structure']:
        structure.append(doc_section_from_dict(e))
    return Doc(
        name=name,
        author=author,
        academic_supervisor=academic_supervisor,
        year=year,
        structure=structure
    )

# make dataclasses from parsing classes
def doc_section_to_dataclass(doc_section: DocSection) -> Chapter:
    chapters = []
    for e in doc_section.structure:
        chapters.append(doc_section_to_dataclass(e))
    return Chapter(
        name=doc_section.name,
        water_content=None,
        words=None,
        symbols=None,
        commonly_used_words=None,
        commonly_used_words_amount=None,
        chapters=chapters
    )

def doc_to_dataclass(doc: Doc) -> Diploma:
    chapters = []
    for e in doc.structure:
        chapters.append(doc_section_to_dataclass(e))
    return Diploma(
        name=doc.name,
        author=doc.author,
        academic_supervisor=doc.academic_supervisor,
        year=doc.year,
        pages=None,
        words=None,
        minimal_disclosure=None,
        load_date=None,
        disclosure_keys=None,
        disclosure_percentage=None,
        shingles=None,
        chapters=chapters        
    )


# some functions for testing
def print_section(section: DocSection, print_text: bool):
    t = ''
    if section.level:
        t = '  ' * section.level
    print(f"{t}len(DocSection.structure): {len(section.structure)} DocSection.name: {section.name} lvl: {section.level}")
    if print_text:
        print(t + section.text.replace('\n', ' '))
    for e in section.structure:
        print_section(e, print_text)

def print_doc_structure(doc: Doc, print_text: bool):
    print('len(Doc.structure):', len(doc.structure), 
          'Doc.name:', doc.name)
    for e in doc.structure:
        print_section(e, print_text)

def print_doc_info(doc: Doc):
    print(f"Doc.name: {doc.name}\nDoc.author: {doc.author}\nDoc.academic_supervisor: {doc.academic_supervisor}\nDoc.year: {doc.year}")

def print_doc(doc: Doc, print_text=False):
    print_doc_info(doc)
    print_doc_structure(doc, print_text)

def save_doc_json(doc: Doc, save_path: str):
    with open(save_path, 'w', encoding ='utf8') as json_file:
        json.dump(doc_to_dict(doc), json_file, indent=4, ensure_ascii=False)

def save_diploma_json(diploma: Diploma, save_path: str):
    with open(save_path, 'w', encoding ='utf8') as json_file:
        json.dump(diploma_to_dict(diploma), json_file, indent=4, ensure_ascii=False)