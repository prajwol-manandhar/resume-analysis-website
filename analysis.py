from firebase_admin import firestore
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_user_skills(userid):
    item = firestore.client().collection('user').document(userid).get().to_dict()['skills']
    user_skill_string = ' '.join(str(e) for e in item)
    return user_skill_string


def get_result(field, user_skill_string, keyword_string):
    content = (user_skill_string, keyword_string)
    cv = CountVectorizer()
    matrix = cv.fit_transform(content)
    singularity_matrix = cosine_similarity(matrix)
    result = (singularity_matrix[1][0]*100)
    result = str(result)
    result = result.split('.', 1)[0]
    # return 'You scored {}% in {} jobs.'.format(result, field)
    return result

def check_result(field, result):
    return 'You scored {}% in {} jobs.'.format(result, field)