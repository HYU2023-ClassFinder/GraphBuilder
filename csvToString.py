import networkx as nx
from networkx import NetworkXNoPath
import csv
import matplotlib.pyplot as plt
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

f2 = open("nst_combined_v2ToString.txt", 'w')

f2.write("[")
for line in rdr:
    f2.write(str(line) + ",\n")
f2.write("]")
f.close()
f2.close()