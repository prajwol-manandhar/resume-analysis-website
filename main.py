import firebase_admin
from firebase_admin import credentials, firestore
import nltk
import docx2txt
from pdfminer.high_level import extract_text


nltk.download('stopwords')
nltk.download('punkt')

# Credentials for the database which is in service_key.json.
cred = credentials.Certificate("service_key.json")
# Initializing firebase admin by passing the credentials for the database.
firebase_admin.initialize_app(cred)

# Array of all the fields present in the database.
fields = ['technology', 'management', 'architect', 'civilservice', 'education', 'engineering', 'journalism', 'law', 'medical', 'science']
keywords = []


# Loop through all the fields and then add all the extracted data in the keywords.
for field in fields:
    data = firestore.client().collection('keyword').document(field).get().to_dict()['key']
    keywords = keywords + data


# Extract text from .docx files
def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None


# Extract text from .pdf files
def extract_text_from_pdf(pdf_path):
    txt = extract_text(pdf_path)
    if txt:
        return txt.replace('\t', ' ')
    return None


# Extract skills from the text
def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)

    # Remove the stop words
    filtered_tokens = [w for w in word_tokens if w not in stop_words]

    # Remove the punctuation
    filtered_tokens = [w for w in word_tokens if w.isalpha()]

    # Generate bigrams and trigrams
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))

    found_skills = set()

    # Search for each token in our skills database
    for token in filtered_tokens:
        if token.lower() in keywords:
            found_skills.add(token)

    # Search for each bigram and trigram in our skills database
    for ngram in bigrams_trigrams:
        if ngram.lower() in keywords:
            found_skills.add(ngram)
    
    return found_skills


def main(file_name):
    file = file_name

    if file.endswith('.pdf'):
        text = extract_text_from_pdf(file)
        skills = extract_skills(text)
        skills = str(skills)
        return skills
    elif file.endswith('.docx'):
        text = extract_text_from_docx(file)
        skills = extract_skills(text)
        skills = str(skills)
        return skills
    else:
        print('Only .pdf or .doc files can be uploaded')

