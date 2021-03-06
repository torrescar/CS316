import urllib, json
import time


# Considerations:
# - Do we want to review classes at Kunshan?
# - CROSS LISTED CLASSES - how should we list these on the website?
# - How should these dictionaries be outputted? JSON?
# - Still need to test whether a professor in different dpts will have correct dpts list_of_values


# GETTING DATABASES
# ------------------------------

    # -----
    # Accesses /curriculum/list_of_values/fieldname/{SUBJECT}
    # Used to find dpt code and description
    # [{u'code': u'AAAS', u'desc': u'African and African American S'}, {u'code': u'ACCOUNTG', u'desc': u'Accounting'}, ...]
def allSubjects():
    url = "https://streamer.oit.duke.edu/curriculum/list_of_values/fieldname/SUBJECT?access_token=70d8b6c4e1ed5cdc532f4ee58397d1b4"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data["scc_lov_resp"]["lovs"]["lov"]["values"]["value"]

    # -----
    # Accesses /curriculum/list_of_values/fieldname/{STRM}
    # Used to decode semester code to semester description
def semDecoder():
    url = "https://streamer.oit.duke.edu/curriculum/list_of_values/fieldname/STRM?access_token=70d8b6c4e1ed5cdc532f4ee58397d1b4"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data["scc_lov_resp"]["lovs"]["lov"]["values"]["value"]

    # -----
    # Accesses /curriculum/courses/crse_id/{crse_id}/crse_offer_nbr/{crse_offer_nbr}
    # Used to find whether a course has been offered before, # credits, course attrs, terms offereds
def courseOfferingDetails(id, offnum):
    url = "https://streamer.oit.duke.edu/curriculum/courses/crse_id/" + id + "/crse_offer_nbr/" + offnum +"?access_token=70d8b6c4e1ed5cdc532f4ee58397d1b4"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data

    # -----
    # Accesses /curriculum/classes/strm/{strm}/crse_id/{crse_id}
    # Used to find professors
def listOfClasses(sem, id, offnum, dictSems):
    semdescr = dictSems[sem]
    semdescr.replace(" ", "%20")
    url = "https://streamer.oit.duke.edu/curriculum/classes/strm/" + sem + "%20-%20" + semdescr + "/crse_id/" + id + "?crse_offer_nbr=" + offnum + "&access_token=70d8b6c4e1ed5cdc532f4ee58397d1b4"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data["ssr_get_classes_resp"]["search_result"]["subjects"]["subject"]["classes_summary"]["class_summary"]

    # -----
    # Accesses /curriculum/courses/subject/{subject}
    # Used to find all course IDs within a given dpt
def allCourseIDs(sub, dictDepts):
    subdescr = dictDepts[sub].dpt
    sub.replace("&", "%26")
    subdescr.replace(" ", "%20")
    url = "https://streamer.oit.duke.edu/curriculum/courses/subject/" + sub + "%20-%20" + subdescr + "?access_token=70d8b6c4e1ed5cdc532f4ee58397d1b4"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data["ssr_get_courses_resp"]["course_search_result"]["subjects"]["subject"]["course_summaries"]["course_summary"]


# BUILDING DICTIONARIES
# ------------------------------

    # -----
    # Build dictDepts: dict[code] = department
    # dictDepts["ECON"] = Economics

class Department:
    def __init__(self, dpt, dptid):
        self.dpt = dpt
        self.dptid = dptid

def getCodes():
    dptList = []
    dptfile = open("currdpts.txt", "r")
    for line in dptfile:
        line = line.strip("\n")
        dptList.append(line)
    dptfile.close()
    return dptList

def build_dictDepts():
    codeList = getCodes()
    data = allSubjects()
    dictDepts = {}
    dptid = 1
    for course in data:
        if course["code"] in codeList:
            dictDepts[course["code"]] = Department(course["desc"], dptid)
            dptid += 1
    return dictDepts

    # -----
    # Build dictCourseDetails: dictCourseDetails[courseid] = Course(subject, catalog_nbr, course_title_long)
    # dictCourseDetails["002432"] = Course("CHINESE", "333", "Advanced Literacy in Chinese", "1", 1.00, ["2012 Fall Term", "2012 Spring Term", ...])
    # NOTE: This dict does not contain any classes > 600 (i.e., GRAD classes) or classes that have not been offered before

class Course:
    def __init__(self, subject, num, title, credits, sems):
        self.subject = subject
        self.num = num
        self.title = title
        self.credits = credits
        self.sems = sems

# Checks to see if a course has been offered before and if the course is at Duke
# Returns False if a course has not been offered before
def check(id, offnum):
    data = courseOfferingDetails(id, offnum)
    if "error" in data.keys():
        return False
    termNonzero = data["ssr_get_course_offering_resp"]["course_offering_result"]
    if int(termNonzero["ssr_terms_offered_count"]) != 0:
        return data["ssr_get_course_offering_resp"]["course_offering_result"]["course_offering"]["campus"] == "DUKE"
    return False

def numCredits(id, offnum):
    data = courseOfferingDetails(id, offnum)
    cred = data["ssr_get_course_offering_resp"]["course_offering_result"]["course_offering"]["units_minimum"]
    cred = cred.strip()
    return float(cred)

def semsOffered(id, offnum):
    data = courseOfferingDetails(id, offnum)
    semsList = []
    if data["ssr_get_course_offering_resp"]["course_offering_result"]["course_offering"]["terms_offered"] is None:
        return []
    else:
        semsData = data["ssr_get_course_offering_resp"]["course_offering_result"]["course_offering"]["terms_offered"]["term_offered"]
        if not(isinstance(semsData, list)):
            semsData = [semsData]
        for sem in semsData:
            semsList.append(sem["strm"])
    return semsList

def build_dictCourseDetails(dictDepts):
    dictCourseDetails = {}
    subcount = 1
    for sub in dictDepts.keys():
        print sub + " subCount: " + str(subcount)
        subcount += 1
        count = 0
        data = allCourseIDs(sub, dictDepts)
        if not(isinstance(data, list)):
            data = [data]
        for course in data:
            courseid = course["crse_id"]
            coursenum = course["catalog_nbr"].strip()
            if len(coursenum) >= 3 and coursenum[2] in "0123456789" and int(coursenum[:3]) >= 600:
                break
            coursetitle = course["course_title_long"]
            courseoffernum = course["crse_offer_nbr"]
            if check(courseid, courseoffernum):
                creds = numCredits(courseid, courseoffernum)
                sems = semsOffered(courseid, courseoffernum)
                print courseid
                count += 1
                #print creds
                #print sems
                if (courseid, courseoffernum) not in dictCourseDetails:
                    dictCourseDetails[(courseid, courseoffernum)] = Course(sub, coursenum, coursetitle, creds, sems)
        print sub + ": " + str(count)
    print "numCourses: " + str(len(dictCourseDetails.keys()))
    return dictCourseDetails

    # -----
    # Build dictDeptCourses: dictDeptCourses[courseid] = [courseattributes]
    # dict["002432"] = ["CCI", "FL", "ALP", "CZ"]
    # If course has no attributes, returns dict[courseid] = []

def getCourseAtts(id, offnum):
    data = courseOfferingDetails(id, offnum)
    if data["ssr_get_course_offering_resp"]["course_offering_result"]["course_offering"]["course_attributes"] is None:
        return []
    else:
        return data["ssr_get_course_offering_resp"]["course_offering_result"]["course_offering"]["course_attributes"]["course_attribute"]

def build_allAtts():
    attList = []
    attfile = open("course_attributes.txt", "r")
    for line in attfile:
        line = line.strip("\n")
        attList.append(line)
    attfile.close()
    return attList

def build_dictCourseAtts(dictCourseDetails):
    dictCourseAtts = {}
    count = 0
    for id, offnum in dictCourseDetails.keys():
        data = getCourseAtts(id, offnum)
        if not(isinstance(data, list)):
            data = [data]
        dictCourseAtts[id] = []
        for att in data:
            if (att["crse_attr"] == "CURR" or att["crse_attr"] == "USE"):
                dictCourseAtts[id].append(att["crse_attr_value"])
                if data != []:
                    count += 1
                    print "current courseatt count: " + str(count)
    print "numCourseAtts: " + str(count)
    return dictCourseAtts

    # -----
    # Build dictProfs: dictProfs[emplid] = Professor(name, [depts])
    # dict["002432"] = ["CCI", "FL", "ALP", "CZ"]
    # Only captures lecture professors

class Professor:
    def __init__(self, name, courses):
        self.name = name
        self.courses = courses

def build_dictSems():
    dictSems = {}
    data = semDecoder()
    for sem in data:
        dictSems[sem["code"]] = sem["desc"]
    return dictSems

def build_dictProfs(dictCourseDetails, dictSems):
    dictProfs = {}
    count = 0
    for id, offnum in dictCourseDetails.keys():
        count += 1
        print "count " + str(count)
        print id
        for sem in dictCourseDetails[(id, offnum)].sems:
            print sem
            data = listOfClasses(sem, id, offnum, dictSems)
            if not(isinstance(data, list)):
                data = [data]
            for section in data:
                dept = section["subject"]
                if section["ssr_component"] == "LEC" or section["ssr_component"] == "SEM":
                    emplid = ""
                    checkMultipleClassPatterns = section["classes_meeting_patterns"]["class_meeting_pattern"]
                    if isinstance(checkMultipleClassPatterns, list) and section["classes_meeting_patterns"]["class_meeting_pattern"][0]["class_instructors"] is None:
                        break
                    if isinstance(checkMultipleClassPatterns, list):
                        for pattern in checkMultipleClassPatterns:
                            instructors = section["classes_meeting_patterns"]["class_meeting_pattern"][0]["class_instructors"]["class_instructor"]
                            if not(isinstance(instructors, list)):
                                instructors = [instructors]
                            for prof in instructors:
                                emplid = prof["emplid"]
                                profname = prof["name_display"]
                                classid = section["crse_id"]
                                if emplid not in dictProfs:
                                    courses = {}
                                    dictProfs[emplid] = Professor(profname, courses)
                                if emplid in dictProfs:
                                    if dept not in dictProfs[emplid].courses.keys():
                                        dictProfs[emplid].courses[dept] = []
                                        dictProfs[emplid].courses[dept].append(classid)
                                    else:
                                        if section["crse_id"] not in dictProfs[emplid].courses[dept]:
                                            dictProfs[emplid].courses[dept].append(classid)
                    elif section["classes_meeting_patterns"]["class_meeting_pattern"]["class_instructors"] is not None:
                        instructors = section["classes_meeting_patterns"]["class_meeting_pattern"]["class_instructors"]["class_instructor"]
                        if not(isinstance(instructors, list)):
                            instructors = [instructors]
                        for prof in instructors:
                            emplid = prof["emplid"]
                            profname = prof["name_display"]
                            classid = section["crse_id"]
                            if emplid not in dictProfs:
                                courses = {}
                                dictProfs[emplid] = Professor(profname, courses)
                            if emplid in dictProfs:
                                if dept not in dictProfs[emplid].courses.keys():
                                    dictProfs[emplid].courses[dept] = []
                                    dictProfs[emplid].courses[dept].append(classid)
                                else:
                                    if section["crse_id"] not in dictProfs[emplid].courses[dept]:
                                        dictProfs[emplid].courses[dept].append(classid)
    print "numProfs: " + str(len(dictProfs.keys()))
    numClasses = 0
    for valobject in dictProfs.values():
        for dept, nbr in valobject.courses.items():
            numClasses += len(nbr)
    print "numClasses: " + str(numClasses)
    return dictProfs

if __name__ == '__main__':
    start_time = time.time()
    dictDepts = build_dictDepts()
    dictCourseDetails = build_dictCourseDetails(dictDepts)
    #dictCourseAtts = build_dictCourseAtts(dictCourseDetails)
    dictSems = build_dictSems()
    dictProfs = build_dictProfs(dictCourseDetails, dictSems)
    print dictProfs
    print dictProfs.keys()
    print dictProfs[dictProfs.keys()[0]].name
    print dictProfs[dictProfs.keys()[0]].courses
    print ("--- %s seconds ---" % (time.time() - start_time))
