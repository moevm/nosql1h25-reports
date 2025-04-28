import io
import os

from flask import Flask, render_template, request, redirect, url_for


from src.diploma_processing.testkit.test_diploma_consts import test_diploma

from src.diploma_processing.stats import CalcStats
from src.repository.diploma_repo import Neo4jDatabase, DiplomaRepository

app = Flask(__name__)

cs = CalcStats()
host = os.getenv('DB_HOST') or 'bolt://localhost'
user = os.getenv('DB_USER') or 'neo4j'
password = os.getenv('DB_PASSWORD') or 'password'

connection = Neo4jDatabase(host, user, password)
repo = DiplomaRepository(connection)


@app.get('/')
def index():
    return redirect(url_for('diploma'))


@app.get('/diploma')
def diploma():
    return render_template('diploma_upload.jinja2')


@app.post('/diploma')
def diploma_upload():
    file = request.files['diploma']
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    diploma = cs.get_diploma_stats(in_memory_file)
    id_diploma = repo.save_diploma(diploma)

    return redirect(url_for('diploma_statistics', diploma_id=id_diploma))


@app.get('/diploma/<int:diploma_id>')
def diploma_statistics(diploma_id: int):
    stats_data = test_diploma[0]

    diploma = repo.load_diploma_data(diploma_id)

    return render_template('general_statistics.jinja2', diploma=stats_data)


@app.get('/search')
def search():
    return render_template('search.jinja2')


@app.get('/search/diploma')
def search_diploma():
    params = request.args.to_dict()

    diplomas = repo.search_diplomas(**params)

    return render_template('diploma_search.jinja2', params = params)


@app.get('/search/chapter')
def search_chapter():
    params = request.args.to_dict(flat=False)

    chapters = repo.search_chapters(**params)

    return render_template('chapter_search.jinja2', chapters=chapters)


if __name__ == '__main__':
    app.run(debug=True)
