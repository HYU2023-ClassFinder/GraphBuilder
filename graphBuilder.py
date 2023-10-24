import networkx as nx
from networkx import NetworkXNoPath
import csv
import matplotlib.pyplot as plt
import random

f = open("nst_combined_predicted_classification_n_est_20.csv", 'r')
rdr = csv.reader(f)

entities = []
triples = []

subEs = []
subTs = []

# trivial = ["Computer_programming", "Computer_science", "Computer", "Image", "Integer", "academic_discipline", "field_of_study", "Personal_computer", "Application_software", "Robot"]
trivial = []

for line in rdr:
    if(len(line[0].split('\t')) == 1):
        continue
    twoEntities = line[0].split('\t')
    if(line[6] == "1" and twoEntities[0] not in trivial and twoEntities[1] not in trivial):
        entities.append(twoEntities[0])
        entities.append(twoEntities[1])
        triples.append((twoEntities[0], twoEntities[1], 1-float(line[1])))
    if(line[6] == "1" and float(line[1]) > 0.9 and twoEntities[0] not in trivial and twoEntities[1] not in trivial):
        subEs.append(twoEntities[0])
        subEs.append(twoEntities[1])
        subTs.append((twoEntities[0], twoEntities[1], 1-float(line[1])))

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

# nx.draw(G, with_labels=True)

# pos = nx.kamada_kawai_layout(G)
# nx.draw(G, pos, with_labels=True, node_size=30)

TRY = 100

for i in range(TRY):
    index0 = random.randint(0, len(entities)-1)
    index1 = random.randint(0, len(entities)-1)

    a = entities[index0]
    b = entities[index1]

    try:
        print(nx.shortest_path(G, a, b))
    except NetworkXNoPath:
        try:
            print(nx.shortest_path(G, b, a))
        except:
            print("NetworkXNoPath from " + a + " to " + b)

pos = nx.kamada_kawai_layout(subG)
nx.draw(subG, pos, with_labels=True, node_size=30)
plt.show()