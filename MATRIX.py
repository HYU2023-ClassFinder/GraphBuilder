import networkx as nx
from networkx import NetworkXNoPath
import csv
import matplotlib.pyplot as plt
import random
import sqlite3
import json

tagMappingv2 = open("tagMappingv2.json", 'r')
mappedTagv2 = json.load(tagMappingv2)
tagMappingv2.close()

f = open("nst_combined_v2.csv", 'r')
rdr = csv.reader(f)

entities = []
triples = []

subEs = []
subTs = []

trivial = ["Programming_language", "Computer_programming", "Computer_science", "Computer", "Image", "Integer", "academic_discipline", "field_of_study", "Personal_computer", "Application_software", "Robot"]
# trivial = []

for line in rdr:
    if(len(line[0].split('\t')) == 1):
        continue

    twoEntities = line[0].split('\t')
    try:
        if(twoEntities[0] not in trivial and twoEntities[1] not in trivial):
            entities.append(mappedTagv2[twoEntities[0]])
            entities.append(mappedTagv2[twoEntities[1]])
            triples.append((mappedTagv2[twoEntities[0]], mappedTagv2[twoEntities[1]], 1-float(line[1])))
    except KeyError:
        continue

    try:
        if(float(line[1]) > 0.9 and twoEntities[0] not in trivial and twoEntities[1] not in trivial):
            subEs.append(mappedTagv2[twoEntities[0]])
            subEs.append(mappedTagv2[twoEntities[1]])
            subTs.append((mappedTagv2[twoEntities[0]], mappedTagv2[twoEntities[1]], 1-float(line[1])))
    except KeyError:
        continue
f.close()

entities = list(set(entities))
subEs = list(set(subEs))

G = nx.DiGraph()
subG = nx.DiGraph()

for entity in entities:
    G.add_node(entity)
for triple in triples:
    G.add_edge(triple[0], triple[1], weight=triple[2])

for subE in subEs:
    subG.add_node(subE)
for subT in subTs:
    subG.add_edge(subT[0], subT[1], weight=subT[2])

print("From: ", end="")
a = input()
a = a.replace(' ', '_')
a = mappedTagv2[a]
print("To: ", end="")
b = input()
b = b.replace(' ', '_')
b = mappedTagv2[b]


print("starThreshhold: ", end="")
starThreshhold = input()
print("regsThreshold: ", end="")
regsThreshold = input()

conn = sqlite3.connect("CScourseDB_EngTag.db")
cur = conn.cursor()

# query = '''
#         select lID, course.name, course.star, cnt 
#         from ( 
#             select row_number() over (order by count(*) desc) as rownum, lectureId as lID, count(*) as cnt 
#             from review, course 
#             where course.id = review.lectureId group by lectureId), course
#         where rownum <= 52 and star >= 4.0 and course.id = lID
#         '''
query = '''
select course.name, tag.tagDetail, course.star, course.regCount
from course, tag
where course.id = tag.lectureId and regCount >= ''' + regsThreshold + ''' and star >= ''' + starThreshhold + '''
'''
minMaxQuery = '''
select min(star), max(star), min(regCount), max(regCount)
from course, tag
where course.id = tag.lectureId and regCount >= 1000 and star >= 4.5
'''
cur.execute(query)
recommendingCandidates = cur.fetchall()

cur.execute(minMaxQuery)
minMax = cur.fetchall()

minStar = minMax[0][0]
maxStar = minMax[0][1]
minRegs = minMax[0][2]
maxRegs = minMax[0][3]

path = nx.shortest_path(G, a, b)
recommedingCourses = [[] for _ in path]

for i in list(range(len(path))):
    for recommendingCandidate in recommendingCandidates:
        try:
            if(mappedTagv2[recommendingCandidate[1].replace(' ', '_')] == path[i]):
                recommedingCourses[i].append((recommendingCandidate[0], (recommendingCandidate[2]-minStar)/(maxStar-minStar), (recommendingCandidate[3]-minRegs)/(maxRegs-minRegs)))
        except KeyError:
            continue

def tempFunc(x):
    return mappedTagv2[x]
mappedTagv2 = dict(map(reversed, mappedTagv2.items()))
path = list(map(tempFunc, path))

print("Curriculum: ", path)
print("-----------------------------")
for i in list(range(len(recommedingCourses))):
    print("for ", path[i])
    recommedingCourses[i] = list(set(recommedingCourses[i]))
    recommedingCourses[i].sort(key=lambda x : -(x[1]+x[2]))

    if(len(recommedingCourses[i]) < 5):
        for j in list(range(len(recommedingCourses[i]))):
            print(recommedingCourses[i][j][0], (recommedingCourses[i][j][1]+recommedingCourses[i][j][2])/2)
    else:
        for j in list(range(0, 5)):
            print(recommedingCourses[i][j][0], (recommedingCourses[i][j][1]+recommedingCourses[i][j][2])/2)
    print("-----------------------------")