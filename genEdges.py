from dataMappedTagv2 import *
from dataNstCombv2 import *
from dataMappedTagv2_codeToTag import *
from dataRecommendingCandidates import *
import json

mappedTagv3 = {}
for key, value in mappedTagv2.items():
    try:
        mappedTagv3[key.upper()] = value
    except RuntimeError:
        continue

entities = set()
triples = []

subEs = set()
subTs = []

trivial = ["Programming_language", "Computer_programming", "Computer_science", "Computer", "Image",
           "Integer", "academic_discipline", "field_of_study", "Personal_computer", "Application_software", "Robot"]

for line in nstCombv2:
    if (len(line[0].split('\t')) == 1):
        continue

    twoEntities = line[0].split('\t')
    try:
        if (twoEntities[0].upper() not in trivial and twoEntities[1].upper() not in trivial):
            entities.add(mappedTagv3[twoEntities[0].upper()])
            entities.add(mappedTagv3[twoEntities[1].upper()])
            triples.append((mappedTagv3[twoEntities[0].upper(
            )], mappedTagv3[twoEntities[1].upper()], 1-float(line[1])))
    except KeyError:
        continue

    try:
        if (float(line[1]) > 0.9 and twoEntities[0].upper() not in trivial and twoEntities[1].upper() not in trivial):
            subEs.add(mappedTagv3[twoEntities[0].upper()])
            subEs.add(mappedTagv3[twoEntities[1].upper()])
            subTs.append((mappedTagv3[twoEntities[0].upper(
            )], mappedTagv3[twoEntities[1].upper()], 1-float(line[1])))
    except KeyError:
        continue

tags_sorted = list(mappedTagv3.keys())
tags_sorted.sort()

out_str = json.dumps({
    "entities": list(entities),
    "sub_entities": list(subEs),
    "triples": triples,
    "sub_triples": subTs,
    "mapped_tags": mappedTagv3,
    "recommending_candidates": recommendingCandidates,
    "tags_sorted": tags_sorted,
    "mapped_tags_code_to_tag": mappedTagv2_codeToTag
})

out_file = open("data.json", "w")
out_file.write(out_str)
out_file.close()
