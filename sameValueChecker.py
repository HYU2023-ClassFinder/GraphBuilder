import json

tagMappingv2 = open("tagMappingv2.json", 'r')
mappedTagv2 = json.load(tagMappingv2)
tagMappingv2.close()

valueList = []
for key, value in mappedTagv2.items():
    if(value not in valueList):
        valueList.append((value))

sameValueCodeList = [[] for _ in valueList]
for i in list(range(len(sameValueCodeList))):
    for key, value in mappedTagv2.items():
        if(value == valueList[i]):
            sameValueCodeList[i].append((key, value))

codeTagMapper = []

for j in list(range(len(sameValueCodeList))):
    print(j, " / ", len(sameValueCodeList), "--------------------------")
    if(len(sameValueCodeList[j]) > 1):
        for i in list(range(len(sameValueCodeList[j]))):
            print(i, sameValueCodeList[j][i])
        print("index: ", end="")
        index = int(input())
        codeTagMapper.append(sameValueCodeList[j][index])
    else:
        codeTagMapper.append(sameValueCodeList[j][0])

codeTagDict = dict(codeTagMapper)

tagMappingv2_codeToTag = open("tagMappingv2_codeToTag.json", 'w')
json.dump(codeTagDict, tagMappingv2_codeToTag, ensure_ascii=False, indent=4)