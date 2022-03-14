import os
from flask import Flask, after_this_request, request, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from main import main
from analysis import get_tech_result, get_management_result, get_softskill_result, result, compare_result
from job import suitable_job


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = ['pdf', 'docx']
app.config['MAXIMUM_FILE_SIZE'] = 2 * 1024 * 1024  # 2 MB


class UploadFileForm(FlaskForm):
    file = FileField('File', validators=[InputRequired()])
    submit = SubmitField('Analyze')


def allowed_extensions(filename):
    if not '.' in filename:
        return False

    f = filename.rsplit('.', 1)[1]

    if f.lower() in app.config['ALLOWED_EXTENSIONS']:
        return True
    else:
        return False


# def allowed_filesize(filename):
#     filesize = os.path.getsize('' + filename)
#     if int(filesize) <= app.config['MAXIMUM_FILE_SIZE']:
#         return True
#     else:
#         return False


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def upload():
    form = UploadFileForm()

    if form.validate_on_submit():
        file = form.file.data  # first grab the file

        if allowed_extensions(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            
            skills = main('static/uploads/' + file.filename)
            skills_result = 'Your skills are: ' + skills
            
            tech_result = get_tech_result(skills)
            management_result = get_management_result(skills)
            compared_result = compare_result(tech_result,management_result)
            softskill_result = get_softskill_result(skills)

            try:
                file = 'static/uploads/' + file.filename
                os.remove(file)
            except Exception as error:
                app.logger.error('Error removing file: ', error)

            return result(skills, compared_result, softskill_result)
        else:
            return 'File extension is not supported. Only upload .docx or .pdf files.'
            
    return render_template('index.html', form=form)


@app.route('/job', methods=['GET', 'POST'])
def job():
    form = UploadFileForm()

    if form.validate_on_submit():
        file = form.file.data  # first grab the file

        if allowed_extensions(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            return suitable_job(main('static/uploads/' + file.filename))

    return render_template('job.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, port='3000')
