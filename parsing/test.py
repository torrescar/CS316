from parse import build_dictDepts, build_dictCourseDetails, build_allAtts

if __name__ == "__main__":
    dictDepts = build_dictDepts()
    #dictCourseDetails = build_dictCourseDetails(dictDepts)
    #dictCourseAtts = build_dictCourseAtts(dictCourseDetails)
    allAtts = build_allAtts()
    print allAtts
    print dictDepts
    print dictDepts["ECON"].dpt
    print dictDepts["ECON"].dptid
