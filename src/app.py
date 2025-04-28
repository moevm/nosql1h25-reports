from flask import Flask, render_template, request, redirect, url_for

from src.diploma_processing.testkit.test_diploma_consts import test_diploma

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
    stats_data = test_diploma[0]

    return render_template('general_statistics.jinja2', diploma=stats_data)


@app.get('/search')
def search():
    return render_template('search.jinja2')


@app.get('/search/diploma')
def search_diploma():
    params = request.args.to_dict()

    return render_template('diploma_search.jinja2', params = [])


# Поиск разделов дипломов
@app.get('/search/chapter')
def search_chapter():
    params = request.args.to_dict(flat=False)

    # Распаковка параметров
    min_id = get_first(params, 'min_id')
    max_id = get_first(params, 'max_id')
    min_id_diploma = get_first(params, 'min_id_diploma')
    max_id_diploma = get_first(params, 'max_id_diploma')
    name = get_first(params, 'section_name')
    min_words = get_first(params, 'min_words')
    max_words = get_first(params, 'max_words')
    min_symbols = get_first(params, 'min_symbols')
    max_symbols = get_first(params, 'max_symbols')
    min_water_content = get_first(params, 'min_water_content')
    max_water_content = get_first(params, 'max_water_content')
    order_by = get_first(params, 'sort_by')

    words = params.get('top_word', []) or None
    chapters = params.get('child_sections', []) or None

    # Приведение типов
    chapters = list(map(int, chapters)) if chapters else None
    words = list(words) if words else None

    # Поиск
    chapters_result = repo.search_chapters(
        min_id=safe_cast(min_id, int),
        max_id=safe_cast(max_id, int),
        min_id_diploma=safe_cast(min_id_diploma, int),
        max_id_diploma=safe_cast(max_id_diploma, int),
        name=name,
        min_words=safe_cast(min_words, int),
        max_words=safe_cast(max_words, int),
        min_symbols=safe_cast(min_symbols, int),
        max_symbols=safe_cast(max_symbols, int),
        min_water_content=safe_cast(min_water_content, float),
        max_water_content=safe_cast(max_water_content, float),
        words=words,
        chapters=chapters,
        order_by=order_by
    )

    results = [
        {
            "id_diploma": ch.id_diploma,
            "id_section": ch.id,
            "section_name": ch.name,
            "water_content": ch.water_content,
            "word_count": ch.words,
            "symbol_count": ch.symbols,
            "top_word": ", ".join(ch.commonly_used_words[:5]),
            "child_sections": ", ".join(map(str, ch.chapters)) if ch.chapters else "-"
        }
        for ch in chapters_result
    ]

    return render_template('chapter_search.jinja2', results=results, params=params)


# Вспомогательные функции
def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def get_first(params, key):
    return params.get(key, [None])[0]


if __name__ == '__main__':
    app.run(debug=True)
