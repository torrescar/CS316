from parse import build_dictDepts, build_dictCourseDetails, build_allAtts, build_dictCourseAtts
import MySQLdb

def insert_depts(dictDepts):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Classes")
    cursor = conn.cursor()

    for code, dpt in dictDepts.items():
        q = "INSERT INTO Department(id, name, abbr) VALUES (%s, %s, %s)"
        cursor.execute(q, (dpt.dptid, dpt.dpt, code))
        conn.commit()
    return

def get_depts():
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Classes")
    cursor = conn.cursor()

    alldepts = "SELECT * FROM Department"
    cursor.execute(alldepts)
    results = cursor.fetchall()
    dict_depts = {}
    for row in results:
        dict_depts[row[2]] = row[0]
    return dict_depts

def insert_courses(dictCourseDetails):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Classes")
    cursor = conn.cursor()

    dict_depts = get_depts()

    for id, det in dictCourseDetails.items():
        q = "INSERT INTO Course(id, dept, num, description, credits) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(q, (id, dict_depts[det.subject], det.num, det.title, det.credits))
        conn.commit()
    return

def insert_atts():
    allAtts = build_allAtts()

    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Classes")
    cursor = conn.cursor()

    for att in allAtts:
        q = "INSERT INTO Attribute(name) VALUES (%s)"
        cursor.execute(q, (att,))
        conn.commit()
    return

def get_att_id():
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Classes")
    cursor = conn.cursor()

    get_att_id = "SELECT * FROM Attribute"
    cursor.execute(get_att_id)
    results = cursor.fetchall()
    dict_attID = {}
    for row in results:
        dict_attID[row[1]] = row[0]
    return dict_attID

def insert_courseAtt(dictCourseDetails):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Classes")
    cursor = conn.cursor()

    dict_attID = get_att_id()

    for id, atts in dictCourseAtts.items():
        for att in atts:
            q = "INSERT INTO Course_Attributes VALUES (%s, %s)"
            cursor.execute(q, (id, dict_attID[att]))
            conn.commit()
    return

if __name__ == "__main__":
    dictDepts = build_dictDepts()
    #insert_depts(dictDepts)
    dictCourseDetails = build_dictCourseDetails(dictDepts)
    dictCourseAtts = build_dictCourseAtts(dictCourseDetails)

    #insert_depts(dictDepts)
    #insert_courses(dictCourseDetails)
    #insert_atts()
    insert_courseAtt(dictCourseDetails)
