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
        pages=5,
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
        ],
        shingles=[
            3009910039063974281,
            7563806526471147744,
            7850915102556697514,
            6738406705845296365,
            6523221563529588383,
            3904788434417142228,
            6970108914954347406,
            4408961805227606693,
            955114944107056676,
            5832621854879736172,
            6642970072674097164,
            535144666985212076,
            837167369269872042,
            649454193406449274,
        ]
    ),
    Diploma(
        id=1,
        name='ОЧЕНЬ ДЛИННОЕ НАЗВАНИЕ ДИПЛОМА 2',
        author='Авторов Б.Б.',
        academic_supervisor='Научруков Б.Б.',
        year=2025,
        words=36,
        pages=7,
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
        ],
        shingles=[
            7579578711281968858,
            2562223532275605288,
            4751378655745306150,
            4128821224416306855,
            2668251532890145301,
            4204626326864875881,
            4869594660343700273,
            9066972562105153886,
            9066795397941182311,
            7674396235708622071,
            6247458571106520196,
            7112072002560255791,
            8098786730820502136,
            7319180713803851700,
            5111194301609589115,
            657447561972040509,
        ]
    )
)
