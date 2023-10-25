f = open("tagClaims_vzscoreUpper40.txt", 'r')

gt = []
tagGT = []

for line in f:
    if(line.split()[1] == "is_preceded_by"):
        gt.append([line.split()[0], line.split()[2]])

f.close()

import json

tagMappingv2 = open("tagMappingv2.json", 'r')
mappedTagv2 = json.load(tagMappingv2)
mappedTagv2 = dict(map(reversed, mappedTagv2.items()))

for _gt in gt:
    tagGT.append([mappedTagv2[_gt[0]], mappedTagv2[_gt[1]]])

tagMappingv2.close()

import csv

f = open('gt.csv','w', newline='')
wr = csv.writer(f)

# triple_name,score,triple_incidence,head_rate,tail_rate,labeled_class,predicted_class
# Xgboost	Rstudio,0.899080017,81.0,0.0058967415043242,0.0063335371713112,-1,1

for _tagGT in tagGT:
    wr.writerow([_tagGT[0]+'\t'+_tagGT[1], 1, -1, -1, -1, 1, 1])

f.close()