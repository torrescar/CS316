from parsetemp import build_dictDepts, build_dictCourseDetails, build_allAtts, build_dictCourseAtts, build_dictSems, build_dictProfs
import MySQLdb

def insert_depts(dictDepts):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()

    for code, dpt in dictDepts.items():
        q = "INSERT INTO Department(id, name, abbr) VALUES (%s, %s, %s)"
        cursor.execute(q, (dpt.dptid, dpt.dpt, code))
        conn.commit()
    return

def get_depts():
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()

    alldepts = "SELECT * FROM Department"
    cursor.execute(alldepts)
    results = cursor.fetchall()
    dict_depts = {}
    for row in results:
        dict_depts[row[2]] = row[0]
    return dict_depts

def insert_courses(dictCourseDetails):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()
    print "INSERTING COURSES!"
    dict_depts = get_depts()
    count = 1
    for id, det in dictCourseDetails.items():
        print "insert course #" + str(count) + " of " + str(len(dictCourseDetails.keys()))
        count += 1
        q = "INSERT INTO Course(id, offnum, dept, num, description, credits) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(q, (id[0], id[1], dict_depts[det.subject], det.num, det.title, det.credits))
        conn.commit()
    return

def insert_atts():
    allAtts = build_allAtts()

    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()

    for att in allAtts:
        q = "INSERT INTO Attribute(name) VALUES (%s)"
        cursor.execute(q, (att,))
        conn.commit()
    return

def get_att_id():
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()

    get_att_id = "SELECT * FROM Attribute"
    cursor.execute(get_att_id)
    results = cursor.fetchall()
    dict_attID = {}
    for row in results:
        dict_attID[row[1]] = row[0]
    return dict_attID

def insert_courseAtt(dictCourseDetails):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()
    print "INSERTING COURSE ATTRIBUTES!"
    dict_attID = get_att_id()
    count = 1
    for id, atts in dictCourseAtts.items():
        for att in atts:
            print "insert courseatt #" + str(count)
            count += 1
            q = "INSERT INTO Course_Attributes VALUES (%s, %s)"
            cursor.execute(q, (id, dict_attID[att]))
            conn.commit()
    return

def insert_profs(dictProfs):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()
    print "INSERTING PROFESSORS!"
    dict_depts = get_depts()
    count = 1
    for emplid, detail in dictProfs.items():
        name = detail.name
        print "insert prof #" + str(count) + " of " + str(len(dictProfs.keys()))
        count += 1
        for dept in detail.courses.keys():
            q = "INSERT INTO Professor(id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id=id"
            cursor.execute(q, (emplid, name))
            conn.commit()
    return

def insert_classes(dictProfs):
    conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Project")
    cursor = conn.cursor()
    print "INSERTING CLASSES!"
    dict_depts = get_depts()
    count = 1
    for emplid, detail in dictProfs.items():
        teacher = emplid
        for dept, classids in detail.courses.items():
            for course in classids:
                print "insert class #" + str(count)
                count += 1
                q = "INSERT INTO Class(course, teacher) VALUES (%s, %s)"
                cursor.execute(q, (course, emplid))
                conn.commit()
    return


if __name__ == "__main__":
    dictDepts = build_dictDepts()
    dictCourseDetails = build_dictCourseDetails(dictDepts)
    dictCourseAtts = build_dictCourseAtts(dictCourseDetails)
    dictSems = build_dictSems()
    dictProfs = build_dictProfs(dictCourseDetails, dictSems)

    #insert_depts(dictDepts)
    #insert_atts()
    insert_courses(dictCourseDetails)
    insert_courseAtt(dictCourseDetails)
    insert_profs(dictProfs)
    insert_classes(dictProfs)
