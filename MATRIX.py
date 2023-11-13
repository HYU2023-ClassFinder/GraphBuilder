import networkx as nx
from networkx import NetworkXNoPath
import csv
import matplotlib.pyplot as plt
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

# trivial한 entity 제거 -> 무의미한 hub가 생기는 것을 방지합니다.
trivial = ["Programming_language", "computer_programming", "Computer_programming", "Computer_science", "Computer", "Image", "Integer", "academic_discipline", "field_of_study", "Personal_computer", "Application_software", "Robot"]
# trivial = []

# entity와 triple list에 내용들 넣기
for line in rdr:
    if(len(line[0].split('\t')) == 1):
        continue

    twoEntities = line[0].split('\t')

    # triple tuple의 세 번째 원소는 score기반 edge의 weight입니다. weight = 1 - score
    try:
        if(twoEntities[0].upper() not in trivial and twoEntities[1].upper() not in trivial):
            entities.append(mappedTagv3[twoEntities[0].upper()])
            entities.append(mappedTagv3[twoEntities[1].upper()])
            triples.append((mappedTagv3[twoEntities[0].upper()], mappedTagv3[twoEntities[1].upper()], 1-float(line[1])))
    except KeyError:
        continue

    # score가 0.9 초과인 triple만 따로 모아 subE와 subT를 만들어봤습니다. -> 쓰지는 않았음
    try:
        if(float(line[1]) > 0.9 and twoEntities[0].upper() not in trivial and twoEntities[1].upper() not in trivial):
            subEs.append(mappedTagv3[twoEntities[0].upper()])
            subEs.append(mappedTagv3[twoEntities[1].upper()])
            subTs.append((mappedTagv3[twoEntities[0].upper()], mappedTagv3[twoEntities[1].upper()], 1-float(line[1])))
    except KeyError:
        continue
f.close()

# 중복 제거
entities = list(set(entities))
subEs = list(set(subEs))

# 그래프 생성하고 node set, edge set 넣습니다.
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

# a = "python"
# b = "gpt"
# starThreshhold = 0
# regsThreshold = 0

print("From: ", end="")
a = input()
a = a.replace(' ', '_').upper()
a = mappedTagv3[a]
print("To: ", end="")
b = input()
b = b.replace(' ', '_').upper()
b = mappedTagv3[b]

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

# 강의 데이터 가져올 쿼리
query = '''
select course.name, tag.tagDetail, course.star, course.regCount
from course, tag
where course.id = tag.lectureId
'''

# minMax normalization할 값들 가져올 쿼리
minMaxQuery = '''
select min(star), max(star), min(regCount), max(regCount)
from course, tag
where course.id = tag.lectureId
'''
cur.execute(query)
recommendingCandidates = cur.fetchall()

cur.execute(minMaxQuery)
minMax = cur.fetchall()

minStar = minMax[0][0]
maxStar = minMax[0][1]
minRegs = minMax[0][2]
maxRegs = minMax[0][3]

# 그래프 G 안의 a에서 출발해서 b로 도착하는 path를 최대 3개까지 찾습니다.
try:
    pathList = []
    X = nx.shortest_simple_paths(G, a, b)
    k = 3
    for counter, path in enumerate(X):
        pathList.append(path)
        if counter == k-1:
            break
except NetworkXNoPath: # path가 없을 때
    print("No path between", a, "and", b)
    pathList = []
except nx.exception.NodeNotFound: # a 또는 b가 없을 때
    print("No", a, "or", b)
    pathList = []

path = [] if len(pathList) < 1 else pathList[0]
secondPath = [] if len(pathList) < 2 else pathList[1]
thirdPath = [] if len(pathList) < 3 else pathList[2]

for _path in pathList:
    print(_path)

tagMappingv2_codeToTag = open("tagMappingv2_codeToTag.json", 'r')
mappedTagv2_codeToTag = dict(json.load(tagMappingv2_codeToTag))
tagMappingv2_codeToTag.close()
mappedTagv2_codeToTag = dict(map(reversed, mappedTagv2_codeToTag.items()))
def tempFunc(x):
    return mappedTagv2_codeToTag[x]

codeG = G.copy()
tagG = nx.relabel_nodes(codeG, mappedTagv2_codeToTag)
pos = nx.spring_layout(tagG, k=1)

codePath = [[] for _ in list(range(len(pathList)))]
_path = [[] for _ in list(range(len(pathList)))]
mains = [[] for _ in list(range(len(pathList)))]
neighbors = [[] for _ in list(range(len(pathList)))]
neighborhoods = [[] for _ in list(range(len(pathList)))]
neighborhoods2 = [[] for _ in list(range(len(pathList)))]
union = [[] for _ in list(range(len(pathList)))]
startAndEnd = []

# 그래프로 시각화하고, 각 path에 대한 추천 강의 목록을 가져옵니다.
for k in list(range(len(pathList)-1, -1, -1)):
    recommedingCourses = [[] for _ in list(range(len(pathList[k])))]

# 별점, 수강생을 minMax normalization
    print(k, list(map(tempFunc, pathList[k])))
    for i in list(range(len(pathList[k]))):
        for recommendingCandidate in recommendingCandidates:
            try:
                if(mappedTagv3[recommendingCandidate[1].replace(' ', '_').upper()] == pathList[k][i]):
                    recommedingCourses[i].append((recommendingCandidate[0], (recommendingCandidate[2]-minStar)/(maxStar-minStar), (recommendingCandidate[3]-minRegs)/(maxRegs-minRegs)))
            except KeyError:
                continue
# normalize한 점수의 평균과 함께, 강의 출력
    print("-----------------------------")
    for i in list(range(len(pathList[k]))):
        print("for ", tempFunc(pathList[k][i]))
        recommedingCourses[i] = list(set(recommedingCourses[i]))
        recommedingCourses[i].sort(key=lambda x : -(x[1]+x[2]))

        if(len(recommedingCourses[i]) < 5):
            for j in list(range(len(recommedingCourses[i]))):
                print(recommedingCourses[i][j][0], (recommedingCourses[i][j][1]+recommedingCourses[i][j][2])/2)
        else:
            for j in list(range(0, 5)):
                print(recommedingCourses[i][j][0], (recommedingCourses[i][j][1]+recommedingCourses[i][j][2])/2)
        print("-----------------------------")

# 그래프 그리기 위한 변수 선언
    codePath[k] = pathList[k].copy()
    _path[k] = list(map(tempFunc, pathList[k]))
    mains[k] = G.subgraph(codePath[k])
    neighborhoods[k] = [[] for _ in _path[k]]
    for i in list(range(len(codePath[k]))):
        for neighborhood in list(codeG.neighbors(codePath[k][i])):
            neighborhoods[k][i].append((neighborhood, codeG[codePath[k][i]][neighborhood]["weight"]))
        neighborhoods[k][i].sort(key=lambda x : x[1])
        while(len(neighborhoods[k][i]) > 2):
            del neighborhoods[k][i][-1]
    neighborhoods[k] = sum(neighborhoods[k], [])
    neighborhoods2[k] = [i[0] for i in neighborhoods[k]]
    neighbors[k] = G.subgraph(neighborhoods2[k])
    union[k] = G.subgraph(codePath[k]+neighborhoods2[k])
    mains[k] = nx.relabel_nodes(mains[k], mappedTagv2_codeToTag)
    neighbors[k] = nx.relabel_nodes(neighbors[k], mappedTagv2_codeToTag)
    union[k] = nx.relabel_nodes(union[k], mappedTagv2_codeToTag)

startAndEnd = G.subgraph([codePath[0][0], codePath[0][-1]])
startAndEnd = nx.relabel_nodes(startAndEnd, mappedTagv2_codeToTag)

# print("is it same?", (_path[2][0] == _path[1][0]))

# 그래프를 예쁘게 그리기 위해, 위아래로 조금씩 노드의 위치를 변경합니다.
for k in list(range(len(pathList)-1, -1, -1)):
    if(k == 2):
        for i in list(range(len(_path[k]))):
            # print(2, _path[k][i])
            pos[_path[k][i]] = [i-len(_path[k])/2, (-1)**i]
    if(k == 1):
        for i in list(range(len(_path[k]))):
            # print(1, _path[k][i])
            pos[_path[k][i]] = [i-len(_path[k])/2, 0.5*(-1)**i]
    if(k == 0):
        for i in list(range(len(_path[k]))):
            # print(0, _path[k][i])
            pos[_path[k][i]] = [i-len(_path[k])/2, (-0.3)**i]

# 시작 노드와 끝 노드의 위치는 고정합니다.
pos[_path[0][0]] = [-len(_path[0])/2, 0]
pos[_path[0][-1]] = [+len(_path[0])/2, 0]

# 그래프를 그립니다.
# 파랑, 초록, 빨강 순으로 path를 보이게 하기 위해, 빨강 path를 먼저 그리고, 초록, 파랑 순으로 그려서
# 파랑이 가장 위에 보이게 합니다.
# neighbors는 각 path들에 속한 노드의 neighbor 집합입니다.
for k in list(range(len(pathList)-1, -1, -1)):
    if(k == 2):
        nx.draw_networkx_nodes(neighbors[k], pos=pos, node_size=75, node_color='grey')
        nx.draw_networkx_labels(neighbors[k], pos=pos, font_size=7, font_color='black')
        nx.draw_networkx_edges(union[k], pos=pos, edge_color='lightgrey')
    if(k == 2):
        nx.draw_networkx_nodes(mains[k], pos=pos, node_size=375, node_color='pink') 
        nx.draw_networkx_labels(mains[k], pos=pos, font_size=7, font_color='red')
        nx.draw_networkx_edges(mains[k], pos=pos, edge_color='red')
    if(k == 1):
        nx.draw_networkx_nodes(mains[k], pos=pos, node_size=375, node_color='yellowgreen') 
        nx.draw_networkx_labels(mains[k], pos=pos, font_size=7, font_color='green')
        nx.draw_networkx_edges(mains[k], pos=pos, edge_color='green')
    if(k == 0):
        nx.draw_networkx_nodes(startAndEnd, pos=pos, node_size=425, node_color='blue') 
        nx.draw_networkx_nodes(mains[k], pos=pos, node_size=375, node_color='skyblue') 
        nx.draw_networkx_labels(mains[k], pos=pos, font_size=7, font_color='blue')
        nx.draw_networkx_edges(mains[k], pos=pos, edge_color='blue')
    
plt.show()