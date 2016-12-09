from parse import courseOfferingDetails, build_dictDepts, build_dictCourseDetails, build_allAtts

if __name__ == "__main__":
    hey = courseOfferingDetails("023888", "1")
    if "error" in hey.keys():
        print "hello"
    dictDepts = build_dictDepts()
    #dictCourseDetails = build_dictCourseDetails(dictDepts)
    #dictCourseAtts = build_dictCourseAtts(dictCourseDetails)
    allAtts = build_allAtts()
    print allAtts
    print dictDepts
    print dictDepts["ECON"].dpt
    print dictDepts["ECON"].dptid
