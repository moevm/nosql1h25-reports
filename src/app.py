from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.get('/')
def index():
    return redirect(url_for('diploma'))


@app.get('/diploma')
def diploma():
    return render_template('layout.jinja2')


@app.post('/diploma')
def upload_diploma():
    file = request.files['diploma']

    return redirect(url_for('diploma_statistics', diploma_id=0))


@app.get('/diploma/<int:diploma_id>')
def diploma_statistics(diploma_id: int):
    return render_template('layout.jinja2')


@app.get('/search')
def search():
    return render_template('layout.jinja2')


@app.get('/search/diploma')
def diploma_search():
    params = request.args.to_dict()

    return render_template('layout.jinja2')


@app.get('/search/chapter')
def chapter_search():
    params = request.args.to_dict()

    return render_template('layout.jinja2')


if __name__ == '__main__':
    app.run(debug=True)
