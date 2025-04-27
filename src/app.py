from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.get('/')
def index():
    return redirect(url_for('diploma'))


@app.get('/diploma')
def diploma():
    return render_template('diploma_upload.jinja2')


@app.post('/diploma')
def diploma_upload():
    file = request.files['diploma']

    return redirect(url_for('diploma_statistics', diploma_id=0))


@app.get('/diploma/<int:diploma_id>')
def diploma_statistics(diploma_id: int):
    stats_data = {
        "author": "Иванов И.И.",
        "title": "Реализация алгоритма",
        "year": 2025,
        "supervisor": "Петров П.П.",
        "pages": 60,
        "words": 10000,
        "topics": [
            {"name": "Тема 1", "coverage": 40},
            {"name": "Тема 2", "coverage": 90},
            {"name": "Тема 3", "coverage": 30},
            {"name": "Тема 4", "coverage": 75}
        ],
        "similar_works": [
            {"name": "Диплом 1", "match": 80},
            {"name": "Диплом 2", "match": 50},
            {"name": "Диплом 3", "match": 40}
        ]
    }


    sections = [
        {
            "title": "Введение",
            "stats": {"words": 328, "characters": 1263, "readability": 30},
            "keywords": {"Алгоритм": 20, "HTTP": 15, "API": 12, "REST": 7},
            "subsections": [
                {
                    "title": "Цели исследования",
                    "stats": {"words": 100, "characters": 500, "readability": 40},
                    "keywords": {"Цель": 5, "Задача": 3},
                },
            ],
        },
        {
            "title": "Содержание",
            "stats": {"words": 450, "characters": 2000, "readability": 40},
            "keywords": {"Метод": 10, "Функция": 8, "Класс": 5},
            "subsections": [
                {
                    "title": "Методология",
                    "stats": {"words": 200, "characters": 1000, "readability": 50},
                    "keywords": {"Метод": 8, "Анализ": 5},
                },
            ],
        },
    ]

    return render_template('general_statistics.jinja2', diploma=stats_data, sections=sections)


@app.get('/search')
def search():
    return render_template('search.jinja2')


@app.get('/search/diploma')
def search_diploma():
    params = request.args.to_dict()

    return render_template('layout.jinja2')


@app.get('/search/chapter')
def search_chapter():
    params = request.args.to_dict()

    return render_template('layout.jinja2')


if __name__ == '__main__':
    app.run(debug=True)
