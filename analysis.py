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
    return result 


def get_management_result(user_skill_string): 
    management_keyword = firestore.client().collection('keyword').document('management').get().to_dict()['key']
    management_keyword_string = ' '.join(str(e) for e in management_keyword)
    result = get_result(user_skill_string, management_keyword_string)
    return result

def compare_result(tech_result, management_result):
    management_score = 'You score ' + management_result + '% in management.'
    tech_score = 'You score ' + tech_result + '% in technology.'
    if int(tech_result) > int(management_result):
        return tech_score + '</br>' + management_score + '</br>' + 'You are more suitable for a tech job.'
    else:
        return tech_score + '</br>' + management_score + '</br>' + 'You are more suitable for a management job.'
    

def get_softskill_result(user_skill_string):
    softskill_keyword = firestore.client().collection('keyword').document('softskill').get().to_dict()['key']
    softskill_keyword_string = ' '.join(str(e) for e in softskill_keyword)
    result = get_result(user_skill_string, softskill_keyword_string)
    if int(result) > 40:
        return 'You have scored ' + result + '% in your softskills. </br> You have good softskills.'
    else:
        return 'You nave scored ' + result + '% in your softskills. </br> You need to work on your softskills.'


def result(skills, compared_result, softskill_result):
    # result = skills + tech_result + '\n' + management_result + '\n' + softskill_result + '\n' + feedback
    skills = 'Your skills are: ' + skills
    result = "</br>".join([skills, compared_result, softskill_result])
    return result