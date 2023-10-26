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

mappedTagv3 = {}
for key, value in mappedTagv2.items():
    try:
        mappedTagv3[key.upper()] = value
    except RuntimeError:
        continue

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
        if(twoEntities[0].upper() not in trivial and twoEntities[1].upper() not in trivial):
            entities.append(mappedTagv3[twoEntities[0].upper()])
            entities.append(mappedTagv3[twoEntities[1].upper()])
            triples.append((mappedTagv3[twoEntities[0].upper()], mappedTagv3[twoEntities[1].upper()], 1-float(line[1])))
    except KeyError:
        continue

    try:
        if(float(line[1]) > 0.9 and twoEntities[0].upper() not in trivial and twoEntities[1].upper() not in trivial):
            subEs.append(mappedTagv3[twoEntities[0].upper()])
            subEs.append(mappedTagv3[twoEntities[1].upper()])
            subTs.append((mappedTagv3[twoEntities[0].upper()], mappedTagv3[twoEntities[1].upper()], 1-float(line[1])))
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
a = a.replace(' ', '_').upper()
a = mappedTagv3[a]
print("To: ", end="")
b = input()
b = b.replace(' ', '_').upper()
b = mappedTagv3[b]

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
where course.id = tag.lectureId and regCount >= ''' + regsThreshold + ''' and star >= ''' + starThreshhold + '''
'''
cur.execute(query)
recommendingCandidates = cur.fetchall()

cur.execute(minMaxQuery)
minMax = cur.fetchall()

minStar = minMax[0][0]
maxStar = minMax[0][1]
minRegs = minMax[0][2]
maxRegs = minMax[0][3]

try:
    pathList = []
    X = nx.shortest_simple_paths(G, a, b)
    k = 4
    for counter, path in enumerate(X):
        pathList.append(path)
        if counter == k-1:
            break
except NetworkXNoPath:
    pathList = []
except nx.exception.NodeNotFound:
    pathList = []

path = [] if len(pathList) < 1 else pathList[0]
secondPath = [] if len(pathList) < 2 else pathList[1]
thirdPath = [] if len(pathList) < 3 else pathList[2]

print(path)
print(secondPath)
print(thirdPath)

recommedingCourses = [[] for _ in path]

for i in list(range(len(path))):
    for recommendingCandidate in recommendingCandidates:
        try:
            if(mappedTagv3[recommendingCandidate[1].replace(' ', '_').upper()] == path[i]):
                recommedingCourses[i].append((recommendingCandidate[0], (recommendingCandidate[2]-minStar)/(maxStar-minStar), (recommendingCandidate[3]-minRegs)/(maxRegs-minRegs)))
        except KeyError:
            continue

tagMappingv2_codeToTag = open("tagMappingv2_codeToTag.json", 'r')
mappedTagv2_codeToTag = dict(json.load(tagMappingv2_codeToTag))
tagMappingv2_codeToTag.close()
mappedTagv2_codeToTag = dict(map(reversed, mappedTagv2_codeToTag.items()))

def tempFunc(x):
    return mappedTagv2_codeToTag[x]

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

codeG = G.copy()
tagG = nx.relabel_nodes(codeG, mappedTagv2_codeToTag)
pos = nx.spring_layout(tagG)

if(len(thirdPath) != 0):
    codePath = thirdPath.copy()
    thirdPath = list(map(tempFunc, thirdPath))
    mains = G.subgraph(codePath)
    neighborhoods = [[] for _ in thirdPath]
    for i in list(range(len(codePath))):
        for neighborhood in list(codeG.neighbors(codePath[i])):
            neighborhoods[i].append((neighborhood, codeG[codePath[i]][neighborhood]["weight"]))
        neighborhoods[i].sort(key=lambda x : x[1])
        while(len(neighborhoods[i]) > 2):
            del neighborhoods[i][-1]
    neighborhoods = sum(neighborhoods, [])
    neighborhoods2 = [i[0] for i in neighborhoods]
    neighbors = G.subgraph(neighborhoods2)
    union = G.subgraph(codePath+neighborhoods2)
    mains = nx.relabel_nodes(mains, mappedTagv2_codeToTag)
    neighbors = nx.relabel_nodes(neighbors, mappedTagv2_codeToTag)
    union = nx.relabel_nodes(union, mappedTagv2_codeToTag)
    # G = nx.relabel_nodes(codeG, mappedTagv2_codeToTag)

    nx.draw_networkx_nodes(neighbors, pos=pos, node_size=75, node_color='grey')
    nx.draw_networkx_labels(neighbors, pos=pos, font_size=7, font_color='black')
    nx.draw_networkx_nodes(mains, pos=pos, node_size=375, node_color='pink') 
    nx.draw_networkx_labels(mains, pos=pos, font_size=7, font_color='red')
    nx.draw_networkx_edges(union, pos=pos, edge_color='lightgrey')
    nx.draw_networkx_edges(mains, pos=pos, edge_color='red')

if(len(secondPath) != 0):
    codePath = secondPath.copy()
    secondPath = list(map(tempFunc, secondPath))
    mains = G.subgraph(codePath)
    neighborhoods = [[] for _ in secondPath]
    for i in list(range(len(codePath))):
        for neighborhood in list(codeG.neighbors(codePath[i])):
            neighborhoods[i].append((neighborhood, codeG[codePath[i]][neighborhood]["weight"]))
        neighborhoods[i].sort(key=lambda x : x[1])
        while(len(neighborhoods[i]) > 2):
            del neighborhoods[i][-1]
    neighborhoods = sum(neighborhoods, [])
    neighborhoods2 = [i[0] for i in neighborhoods]
    neighbors = G.subgraph(neighborhoods2)
    union = G.subgraph(codePath+neighborhoods2)
    mains = nx.relabel_nodes(mains, mappedTagv2_codeToTag)
    neighbors = nx.relabel_nodes(neighbors, mappedTagv2_codeToTag)
    union = nx.relabel_nodes(union, mappedTagv2_codeToTag)
    # G = nx.relabel_nodes(codeG, mappedTagv2_codeToTag)

    # nx.draw_networkx_nodes(neighbors, pos=pos, node_size=75, node_color='grey')
    # nx.draw_networkx_labels(neighbors, pos=pos, font_size=7, font_color='black')
    nx.draw_networkx_nodes(mains, pos=pos, node_size=375, node_color='yellowgreen') 
    nx.draw_networkx_labels(mains, pos=pos, font_size=7, font_color='green')
    # nx.draw_networkx_edges(union, pos=pos, edge_color='lightgrey')
    nx.draw_networkx_edges(mains, pos=pos, edge_color='green')

if(len(path) != 0):
    codePath = path.copy()
    path = list(map(tempFunc, path))
    mains = G.subgraph(codePath)
    neighborhoods = [[] for _ in path]
    for i in list(range(len(codePath))):
        for neighborhood in list(codeG.neighbors(codePath[i])):
            neighborhoods[i].append((neighborhood, codeG[codePath[i]][neighborhood]["weight"]))
        neighborhoods[i].sort(key=lambda x : x[1])
        while(len(neighborhoods[i]) > 2):
            del neighborhoods[i][-1]
    neighborhoods = sum(neighborhoods, [])
    neighborhoods2 = [i[0] for i in neighborhoods]
    neighbors = G.subgraph(neighborhoods2)
    union = G.subgraph(codePath+neighborhoods2)
    mains = nx.relabel_nodes(mains, mappedTagv2_codeToTag)
    neighbors = nx.relabel_nodes(neighbors, mappedTagv2_codeToTag)
    union = nx.relabel_nodes(union, mappedTagv2_codeToTag)
    # G = nx.relabel_nodes(codeG, mappedTagv2_codeToTag)

    # nx.draw_networkx_nodes(neighbors, pos=pos, node_size=75, node_color='grey')
    # nx.draw_networkx_labels(neighbors, pos=pos, font_size=7, font_color='black')
    nx.draw_networkx_nodes(mains, pos=pos, node_size=375, node_color='skyblue') 
    nx.draw_networkx_labels(mains, pos=pos, font_size=7, font_color='blue')
    # nx.draw_networkx_edges(union, pos=pos, edge_color='lightgrey')
    nx.draw_networkx_edges(mains, pos=pos, edge_color='blue')
    
plt.show()