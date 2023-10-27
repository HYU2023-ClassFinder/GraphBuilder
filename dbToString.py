import sqlite3

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

courseQuery = '''
select course.name, course.star, course.regCount, course.id
from course'''

tagQuery = '''
select tag.lectureId, tag.tagDetail
from tag'''

minMaxQuery = '''
select min(star), max(star), min(regCount), max(regCount)
from course, tag
where course.id = tag.lectureId '''

cur.execute(courseQuery)
courseData = cur.fetchall()

cur.execute(tagQuery)
tagData = cur.fetchall()

cur.execute(minMaxQuery)
minMax = cur.fetchall()

minStar = minMax[0][0]
maxStar = minMax[0][1]
minRegs = minMax[0][2]
maxRegs = minMax[0][3]

recommendingCandidates = []

for _courseData in courseData:
    courseTag = []
    for _tagData in tagData:
        if(_tagData[0] == _courseData[3]):
            courseTag.append(_tagData[1])
    recommendingCandidates.append([_courseData[0], _courseData[1], _courseData[2], courseTag])

print(recommendingCandidates[0])
print(recommendingCandidates[1])
print(recommendingCandidates[2])
    
f2 = open("recommendingCandidatesToString.txt", 'w', encoding='utf-8')

f2.write("[")
for i in list(range(len(recommendingCandidates))):
    f2.write(str(recommendingCandidates[i]) + ",\n")
    # f2.write('[' + recommendingCandidates[i][0] + ', ' + str(recommendingCandidates[i][1]) + ', ' + str(recommendingCandidates[i][2]) + ', ' + str(recommendingCandidates[i][3]) + '],\n')
# f2.write(str(recommendingCandidates[0]))
f2.write("]")
f2.close()