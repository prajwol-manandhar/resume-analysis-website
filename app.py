import os
from flask import Flask, after_this_request, request, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from firebase_admin import firestore
from main import main
from analysis import get_result


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
            
            skills = main('static/uploads/' + file.filename.replace(' ', '_'))

            fields = ['technology', 'management', 'architect', 'civilservice', 'education', 'engineering', 'journalism', 'law', 'medical', 'science']
            feedback = 'Your skills are {}. \n'.format(skills)

            for field in fields:
                keyword = firestore.client().collection('keyword').document(field).get().to_dict()['key']
                keyword_string = ' '.join(str(e) for e in keyword)
                result = get_result(field, skills, keyword_string)
                feedback = feedback + str(result) + '</br>'

            try:
                file = 'static/uploads/' + file.filename
                os.remove(file)
            except Exception as error:
                app.logger.error('Error removing file: ', error)

            return render_template('feedback.html', feedback=feedback)
        else:
            return 'File extension is not supported. Only upload .docx or .pdf files.'
            
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, port='3000')
