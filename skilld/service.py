# -*- coding: utf-8 -*-
import json
with open('professions.json','r') as infile:
    matchframe = json.load(infile)

def getprofession(unmatchedprofessionstring):
    matched = False
    professionstring = unmatchedprofessionstring.replace(' ','').lower().strip()
    inprofessions = professionstring.replace('/',',').replace('food and','foodand').replace(' and ',',').split(',')
    outprofessions = list()
    for profession in inprofessions:
        for row in matchframe:
            if profession in matchframe[row].values():
                prof = dict()
                prof['title']=row
                prof['profession']=profession
                prof['confidence']=1.0
                outprofessions.append(prof)
    if outprofessions:
        return outprofessions
    else:
        return None


def handler(event, context):
    if context:
        dbenv = str(context.invoked_function_arn).split(":")
        global env
        env = dbenv[-1]
    else:
        env = 'test'
    professions = getprofession(event['profession'])
    return professions

