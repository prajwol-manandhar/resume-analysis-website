import os
from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from pyparsing import And
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from main import main
from analysis import get_tech_result, get_management_result, get_softskill_result, feedback


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = ['pdf', 'docx']
app.config['MAXIMUM_FILE_SIZE'] = 2 * 1024 * 1024 # 2 MB


class UploadFileForm(FlaskForm):
    file = FileField('File', validators=[InputRequired()])
    submit = SubmitField('Upload File')


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
        file = form.file.data # first grab the file
        if allowed_extensions(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))     
            skills = main('static/uploads/' + file.filename)
            
            tech_result = get_tech_result(skills)
            management_result = get_management_result(skills)
            softskill_result = get_softskill_result(skills)

            result = feedback(tech_result, management_result, softskill_result)
            
            return result
        else:
            return 'File extension is not supported. Only upload .docx or .pdf files.'
    return render_template('index.html', form=form)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    form = UploadFileForm()
    file = form.validate_on_submit()
    print(file)


@app.route('/delete') 
def remove():
    form = UploadFileForm()
    file = form.file.data
    file.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    

if __name__ == '__main__':
    app.run(debug=True, port='3000')