from firebase_admin import credentials,firestore
from main import main

cred = credentials.Certificate("service_key.json")

def suitable_job(user_skills):
    jobs = firestore.client().collection(u'job').stream()
    for job in jobs:
        skills = u'{}'.format(job.to_dict()['skills'])
        for skill in user_skills:
            if skill in skills:
                return skills



