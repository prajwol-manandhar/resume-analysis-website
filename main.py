import firebase_admin
from firebase_admin import credentials, firestore
import nltk
import docx2txt
from pdfminer.high_level import extract_text
from analysis import get_tech_result, get_management_result, get_softskill_result

nltk.download('stopwords')
nltk.download('punkt')

cred = credentials.Certificate("service_key.json")
firebase_admin.initialize_app(cred)


tech_keyword = firestore.client().collection('keyword').document('technology').get().to_dict()['key']
management_keyword = firestore.client().collection('keyword').document('management').get().to_dict()['key']
softskill_keyword = firestore.client().collection('keyword').document('softskill').get().to_dict()['key']
all_keywords = tech_keyword + management_keyword + softskill_keyword


def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

def extract_text_from_pdf(pdf_path):
    txt = extract_text(pdf_path)
    if txt:
        return txt.replace('\t', ' ')
    return None


def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)

    # remove the stop words
    filtered_tokens = [w for w in word_tokens if w not in stop_words]

    # remove the punctuation
    filtered_tokens = [w for w in word_tokens if w.isalpha()]

    # generate bigrams and trigrams
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))

    found_skills = set()

    # search for each token in our skills database
    for token in filtered_tokens:
        if token.lower() in all_keywords:
            found_skills.add(token)

    # search for each bigram and trigram in our skills database
    for ngram in bigrams_trigrams:
        if ngram.lower() in all_keywords:
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

