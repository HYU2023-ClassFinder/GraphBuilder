import networkx as nx
from networkx import NetworkXNoPath
import matplotlib.pyplot as plt
from dataMappedTagv2 import *
from dataNstCombv2 import *
from dataMappedTagv2_codeToTag import *
from dataRecommendingCandidates.py import *

fig, ax = plt.subplots()

mappedTagv3 = {}
for key, value in mappedTagv2.items():
	try:
		mappedTagv3[key.upper()] = value
	except RuntimeError:
		continue

entities = []
triples = []

subEs = []
subTs = []

trivial = ["Programming_language", "Computer_programming", "Computer_science", "Computer", "Image", "Integer", "academic_discipline", "field_of_study", "Personal_computer", "Application_software", "Robot"]

for line in nstCombv2:
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
# f.close()

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

# a = "python"
# b = "gpt"
# starThreshhold = "0"
# regsThreshold = "0"

a = input()
print("From: ", a, end="")
a = a.replace(' ', '_').upper()
a = mappedTagv3[a]

b = input()
print("To: ", b, end="")
b = b.replace(' ', '_').upper()
b = mappedTagv3[b]

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

mappedTagv2_codeToTag = dict(map(reversed, mappedTagv2_codeToTag.items()))

def tempFunc(x):
	return mappedTagv2_codeToTag[x]

print(list(map(tempFunc, path)))
print(list(map(tempFunc, secondPath)))
print(list(map(tempFunc, thirdPath)))

codeG = G.copy()
tagG = nx.relabel_nodes(codeG, mappedTagv2_codeToTag)
pos = nx.spring_layout(tagG)

recommedingCourses = [[] for _ in path]

def tempFunc2(x):
	return x.replace(' ', '_').upper()

def tempFunc3(x):
	return mappedTagv2[x]

for k in list(range(len(pathList)-1, -1, -1)):
	print(k, list(map(tempFunc, pathList[k])))
    for i in list(range(len(pathList[k]))):
        for recommendingCandidate in recommendingCandidates:
            try:
				if()
                if(pathList[k][i] in list(map(tempFunc3, recommendingCandidate[3]))):
                    recommedingCourses[i].append((recommendingCandidate[0], (recommendingCandidate[1])/(5), (recommendingCandidate[2])/(1418723)))
            except KeyError:
                continue

    print("-----------------------------")
    for i in list(range(len(recommedingCourses))):
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

	codePath = pathList[k].copy()
	_path = list(map(tempFunc, pathList[k]))
	mains = G.subgraph(codePath)
	neighborhoods = [[] for _ in _path]
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

	if(k == 0):
		nx.draw_networkx_nodes(neighbors, pos=pos, node_size=75, node_color='grey')
		nx.draw_networkx_labels(neighbors, pos=pos, font_size=7, font_color='black')
		nx.draw_networkx_edges(union, pos=pos, edge_color='lightgrey')
	if(k == 2):
		nx.draw_networkx_nodes(mains, pos=pos, node_size=375, node_color='pink') 
		nx.draw_networkx_labels(mains, pos=pos, font_size=7, font_color='red')
		nx.draw_networkx_edges(mains, pos=pos, edge_color='red')
	if(k == 1):
		nx.draw_networkx_nodes(mains, pos=pos, node_size=375, node_color='yellowgreen') 
		nx.draw_networkx_labels(mains, pos=pos, font_size=7, font_color='green')
		nx.draw_networkx_edges(mains, pos=pos, edge_color='green')
	if(k == 0):
		nx.draw_networkx_nodes(mains, pos=pos, node_size=375, node_color='skyblue') 
		nx.draw_networkx_labels(mains, pos=pos, font_size=7, font_color='blue')
		nx.draw_networkx_edges(mains, pos=pos, edge_color='blue')
	
	
pyscript.write('graph', fig)