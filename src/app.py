import io
import os

from flask import Flask, render_template, request, redirect, url_for, send_file, session

from src.diploma_processing.stats import CalcStats
from src.repository.diploma_repo import Neo4jDatabase, DiplomaRepository

app = Flask(__name__)

app.secret_key = os.getenv('SESSION_KEY', 'example').encode()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'example')

cs = CalcStats()
host = os.getenv('DB_HOST', 'bolt://localhost')
user = os.getenv('DB_USER', 'neo4j')
password = os.getenv('DB_PASSWORD', 'password')

connection = Neo4jDatabase(host, user, password)
repo = DiplomaRepository(connection)

dumps = {}


@app.get('/')
def diploma_index():
    return diploma()


@app.get('/diploma')
def diploma():
    return render_template('diploma_upload.jinja2')


@app.post('/diploma')
def diploma_upload():
    file = request.files['diploma']
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)

    try:
        diploma = cs.get_diploma_stats(in_memory_file)
        id_diploma = repo.save_diploma(diploma)

        return redirect(url_for('diploma_statistics', diploma_id=id_diploma))
    except Exception:
        return 'BAD REQUEST', 400


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

    diplomas, count = repo.search_diplomas(**params)

    return render_template('diploma_search.jinja2', diplomas=diplomas, total_count=count)


@app.get('/search/chapter')
def search_chapter():
    params = request.args.to_dict()
    params = {key: value for (key, value) in params.items() if value is not None and value != ''}
    if 'words' in params:
        params['words'] = params['words'].split()
    if 'chapters' in params:
        params['chapters'] = params['chapters'].split()

    chapters, count = repo.search_chapters(**params)

    return render_template('chapter_search.jinja2', chapters=chapters, total_count=count)


@app.get('/dump')
def dump():
    if 'username' in session:
        return render_template('dump.jinja2')
    else:
        return render_template('login.jinja2')


@app.post('/login')
def login():
    user_password = request.form['password']

    if user_password and user_password == ADMIN_PASSWORD:
        session['username'] = 'OK'
        return redirect(url_for('dump'))
    else:
        return 'UNAUTHORIZED', 401


@app.post('/import')
def import_db():
    file = request.files['dump']
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)

    dump_id = max(dumps.keys()) + 1 if len(dumps.keys()) > 0 else 0
    dumps[dump_id] = in_memory_file

    result = repo.import_by_url(
        f"http://{'app' if os.getenv('DOCKER_APP') else 'host.docker.internal'}:5000{url_for('send_dump', file_id=dump_id)}")
    del dumps[dump_id]

    if result:
        return 'OK', 200
    else:
        return 'BAD REQUEST', 400


@app.get('/dump/file/<int:file_id>')
def send_dump(file_id: int):
    dump_file = dumps[file_id]
    dump_file.seek(0)

    return send_file(dump_file, as_attachment=True, download_name='dump.json')


@app.get('/dump/file')
def send_main_dump():
    return send_file('dump.json', as_attachment=True, download_name='dump.json')


@app.get('/export')
def export_db():
    file = repo.export()

    return send_file(file, mimetype='json', as_attachment=True, download_name='dump.json')


@app.before_request
def init():
    app.before_request_funcs[None].remove(init)
    if len(repo) == 0:
        app.logger.info('ok')
        repo.import_by_url(
            f"http://{'app' if os.getenv('DOCKER_APP') else 'host.docker.internal'}:5000{url_for('send_main_dump')}")


if __name__ == '__main__':
    app.run(debug=True, port=5000)
