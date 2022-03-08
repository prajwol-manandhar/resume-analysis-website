from firebase_admin import firestore
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_result(user_skill_string, keyword_string):
    content = (user_skill_string, keyword_string)
    cv = CountVectorizer()
    matrix = cv.fit_transform(content)
    singularity_matrix = cosine_similarity(matrix)
    result = (singularity_matrix[1][0]*100)
    result = str(result)
    result = result.split('.', 1)[0]
    return result


def get_tech_result(user_skill_string):
    tech_keyword = firestore.client().collection('keyword').document('technology').get().to_dict()['key']
    tech_keyword_string = ' '.join(str(e) for e in tech_keyword)
    result = get_result(user_skill_string, tech_keyword_string)
    print('You are ' + result + '% compatible for tech jobs.')
    return result


def get_management_result(user_skill_string): 
    management_keyword = firestore.client().collection('keyword').document('management').get().to_dict()['key']
    management_keyword_string = ' '.join(str(e) for e in management_keyword)
    result = get_result(user_skill_string, management_keyword_string)
    print('You are ' + result + '% compatible for management jobs.')
    return result


def get_softskill_result(user_skill_string):
    softskill_keyword = firestore.client().collection('keyword').document('softskill').get().to_dict()['key']
    softskill_keyword_string = ' '.join(str(e) for e in softskill_keyword)
    result = get_result(user_skill_string, softskill_keyword_string)
    print('You score ' + result + '% in softskills.')
    return result


def feedback(tech_result, management_result, softskill_result):
    if management_result > tech_result:
        return 'You are more suitable for a management job'
    else:
        return 'You are more suitable for a tech job.'

    if softskill_result > '40':
        print('You have good soft skills.')
    else:
        print('You need to work on your soft skills.')
