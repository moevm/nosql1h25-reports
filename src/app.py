import io
import os

from flask import Flask, render_template, request, redirect, url_for, send_file

from src.diploma_processing.stats import CalcStats
from src.repository.diploma_repo import Neo4jDatabase, DiplomaRepository

app = Flask(__name__)

cs = CalcStats()
host = os.getenv('DB_HOST') or 'bolt://localhost'
user = os.getenv('DB_USER') or 'neo4j'
password = os.getenv('DB_PASSWORD') or 'password'

connection = Neo4jDatabase(host, user, password)
repo = DiplomaRepository(connection)

dumps = {}


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
    diploma = repo.load_diploma_data(diploma_id)

    return render_template('general_statistics.jinja2', diploma=diploma)


@app.get('/search')
def search():
    return render_template('search.jinja2')


@app.get('/search/diploma')
def search_diploma():
    params = request.args.to_dict()
    params = {key: value for (key, value) in params.items() if value is not None and value != ''}
    if 'chapters' in params:
        params['chapters'] = params['chapters'].split()

    diplomas = repo.search_diplomas(**params)

    return render_template('diploma_search.jinja2', diplomas=diplomas)


@app.get('/search/chapter')
def search_chapter():
    params = request.args.to_dict()
    params = {key: value for (key, value) in params.items() if value is not None and value != ''}
    if 'words' in params:
        params['words'] = params['words'].split()
    if 'chapters' in params:
        params['chapters'] = params['chapters'].split()

    chapters = repo.search_chapters(**params)

    return render_template('chapter_search.jinja2', chapters=chapters)


@app.get('/dump')
def dump():
    return render_template('dump.jinja2')


@app.post('/import')
def import_db():
    file = request.files['dump']
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)

    dump_id = max(dumps.keys()) + 1 if len(dumps.keys()) > 0 else 0
    dumps[dump_id] = in_memory_file

    repo.import_by_url(
        f"http://{'app' if os.getenv('DOCKER_APP') else 'host.docker.internal'}:5000{url_for('send_dump', file_id=dump_id)}")

    return redirect(url_for('dump'))


@app.get('/dump/file/<int:file_id>')
def send_dump(file_id: int):
    dump_file = dumps[file_id]
    del dumps[file_id]
    dump_file.seek(0)

    return send_file(dump_file, as_attachment=True, download_name='dump.json')


@app.get('/export')
def export_db():
    file = repo.export()

    return send_file(file, mimetype='json', as_attachment=True, download_name='dump.json')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
