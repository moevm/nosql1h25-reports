import datetime

from src.diploma_processing.data_types import Chapter, Diploma

test_diploma = (
    Diploma(
        id=0,
        name='ОЧЕНЬ ДЛИННОЕ НАЗВАНИЕ ДИПЛОМА 1',
        author='Авторов А.А.',
        academic_supervisor='Научруков А.А.',
        year=2024,
        words=24,
        load_date=datetime.datetime.fromisoformat('2025-04-25T20:01:25.807687'),
        chapters=[
            Chapter(
                id=0,
                id_diploma=0,
                name='ВВЕДЕНИЕ',
                water_content=85,
                words=2,
                symbols=11,
                commonly_used_words=['это', 'введение'],
                commonly_used_words_amount=[1, 1],
                chapters=[]
            ),
            Chapter(
                id=1,
                id_diploma=0,
                name='Структура',
                water_content=60,
                words=15,
                symbols=66,
                commonly_used_words=['это', 'раздел', 'пояснения'],
                commonly_used_words_amount=[2, 1, 1],
                chapters=[
                    Chapter(
                        id=3,
                        id_diploma=0,
                        name='Раздел 1',
                        water_content=70,
                        words=5,
                        symbols=16,
                        commonly_used_words=['это', 'раздел'],
                        commonly_used_words_amount=[2, 1],
                        chapters=[]
                    ),
                    Chapter(
                        id=4,
                        id_diploma=0,
                        name='Раздел 2',
                        water_content=50,
                        words=10,
                        symbols=50,
                        commonly_used_words=['это', 'пояснения'],
                        commonly_used_words_amount=[2, 1],
                        chapters=[]
                    )
                ]
            ),
            Chapter(
                id=2,
                id_diploma=0,
                name='ЗАКЛЮЧЕНИЕ',
                water_content=80,
                words=7,
                symbols=60,
                commonly_used_words=['наконец', 'заключение'],
                commonly_used_words_amount=[2, 1],
                chapters=[]
            )
        ]
    ),
    Diploma(
        id=1,
        name='ОЧЕНЬ ДЛИННОЕ НАЗВАНИЕ ДИПЛОМА 2',
        author='Авторов Б.Б.',
        academic_supervisor='Научруков Б.Б.',
        year=2025,
        words=36,
        load_date=datetime.datetime.fromisoformat('2025-04-25T20:14:56.709861'),
        chapters=[
            Chapter(
                id=5,
                id_diploma=1,
                name='ВВЕДЕНИЕ',
                water_content=50,
                words=10,
                symbols=45,
                commonly_used_words=['длинное', 'введение', 'дипломной', 'работы'],
                commonly_used_words_amount=[2, 2, 1, 1],
                chapters=[]
            ),
            Chapter(
                id=6,
                id_diploma=1,
                name='Структура',
                water_content=50,
                words=19,
                symbols=83,
                commonly_used_words=['это', 'пояснения', 'первого', 'первый', 'раздел'],
                commonly_used_words_amount=[5, 2, 2, 1, 1],
                chapters=[
                    Chapter(
                        id=8,
                        id_diploma=1,
                        name='Раздел 1',
                        water_content=60,
                        words=6,
                        symbols=23,
                        commonly_used_words=['это', 'раздел', 'первый'],
                        commonly_used_words_amount=[2, 1, 1],
                        chapters=[]
                    ),
                    Chapter(
                        id=9,
                        id_diploma=1,
                        name='Раздел 2',
                        water_content=40,
                        words=13,
                        symbols=60,
                        commonly_used_words=['это', 'пояснения', 'первого', 'раздела', 'диплома'],
                        commonly_used_words_amount=[3, 2, 2, 1, 1],
                        chapters=[]
                    )
                ]
            ),
            Chapter(
                id=7,
                id_diploma=1,
                name='ЗАКЛЮЧЕНИЕ',
                water_content=80,
                words=7,
                symbols=60,
                commonly_used_words=['наконец', 'заключение'],
                commonly_used_words_amount=[2, 1],
                chapters=[]
            )
        ]
    )
)
