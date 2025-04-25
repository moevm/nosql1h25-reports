import json
from datetime import datetime

from src.diploma_processing.data_types import Chapter, Diploma


# serialize/deserialize Chapter
def chapter_to_dict(chapter: Chapter) -> dict:
    chapter_dict = chapter.__dict__.copy()
    chapter_dict['chapters'] = []
    for e in chapter.chapters:
        chapter_dict['chapters'].append(chapter_to_dict(e))
    return chapter_dict

def chapter_from_dict(chapter: dict) -> Chapter:
    id = chapter['id']
    id_diploma=chapter['id_diploma']
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
        id=id,
        id_diploma=id_diploma,
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
    id = diploma['id']
    name = diploma['name']
    author = diploma['author']
    academic_supervisor = diploma['academic_supervisor']
    year = diploma['year']
    words = diploma['words']
    if diploma.get('load_date') and diploma['load_date']:
        load_date = datetime.fromisoformat(diploma['load_date'])
    else:
        load_date = diploma['load_date']
    chapters = []
    for e in diploma['chapters']:
        chapters.append(chapter_from_dict(e))
    return Diploma(
        id=id,
        name=name,
        author=author,
        academic_supervisor=academic_supervisor,
        year=year,
        words=words,
        load_date=load_date,
        chapters=chapters
    )


def save_diploma_json(diploma: Diploma, save_path: str):
    with open(save_path, 'w', encoding ='utf8') as json_file:
        json.dump(diploma_to_dict(diploma), json_file, indent=4, ensure_ascii=False)