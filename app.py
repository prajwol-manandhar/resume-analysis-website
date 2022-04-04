import os
from flask import Flask, after_this_request, request, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from firebase_admin import firestore
from main import main
from analysis import get_result, check_result

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
            # Save the uploaded file in the directed path.
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))

            # Call main function in main.py by passing the file.
            skills = main('static/uploads/' + file.filename.replace(' ', '_'))

            # Array of the fields present in the database.
            fields = ['technology', 'management', 'architect', 'civilservice', 'education', 'engineering', 'journalism', 'law', 'medical', 'science']
            result = {}
            # Initialization of feedback as a string.
            feedback = 'Your skills are {}. </br>'.format(skills)

            # Loops through all the fields in the database and then matches the keyword.
            for field in fields:
                # Get keywords from the database.
                keyword = firestore.client().collection('keyword').document(field).get().to_dict()['key']
                # Convert the keywords into string.
                keyword_string = ' '.join(str(e) for e in keyword)
                # Call the get_result function in the analyze.py and the store it in form of key, value i.e dictionary.
                result[field] = int(get_result(field, skills, keyword_string))
            
            # Sort the dictionary into descending order.
            sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)

            # Loops through the sorted dictionary and then assign the results if not equal to 0.
            for key, value in sorted_result:
                checked_result = check_result(key, value)
                if value == 0:
                    break
                # Concatenate the result into the feedback.
                feedback = feedback + str(checked_result) + '</br>'

            # Remove the uploaded file after analyzing it.
            # try:
            #     file = 'static/uploads/' + file.filename.replace(' ', '_')
            #     os.remove(file)
            # except Exception as error:
            #     app.logger.error('Error removing file: ', error)

            return feedback
            # In order to return the webpage :
            # return render_template('feedback.html', feedback = feedback)

        else:
            return 'File extension is not supported. Only upload .docx or .pdf files.'
    
    # Return index.html where form is passed as form itself.
    return render_template('index.html', form=form)


if __name__ == '__main__':
    # Run the app on port 3000 while debug is True. 
    app.run(debug=True, port='3000')
