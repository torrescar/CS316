# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sample App Engine application demonstrating how to connect to Google Cloud SQL
using App Engine's native unix socket or using TCP when running locally.
For more information, see the README.md.
"""

# [START all]
from flask import Flask, render_template, request, json
import os
import MySQLdb
import app 

app = Flask(__name__)

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')
CLOUDSQL_DB = os.environ.get('CLOUDSQL_DB')


def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD,
            db=CLOUDSQL_DB)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)
    return db


@app.route("/")
def main():
    return render_template('home.html')

@app.route("/rate")
def rate():
    conn = connect_to_cloudsql()
    cursor = conn.cursor()
    q = "SELECT abbr, Course.id, num, description FROM Course, Department WHERE Course.dept = Department.id"
    cursor.execute(q)
    data = cursor.fetchall()
    return render_template('rate.html', courses=data)

@app.route("/search")
def search():
    conn = connect_to_cloudsql()
    cursor = conn.cursor()
    q = "SELECT name, id, abbr from Department"
    cursor.execute(q)
    data = cursor.fetchall()
    return render_template('search.html', courses=data)

@app.route('/search_course/<int:myClass>',methods=['POST', 'GET'])
def search_course(myClass):
    try:
        # read the posted values from the UI
        _class = str(myClass)
        # validate the received values
        if True:
            conn = connect_to_cloudsql()
            cursor = conn.cursor()
            #cursor.execute("SELECT * FROM Department")
            q = "SELECT * from Course WHERE id = %s"
            cursor.execute(q, (_class))
            #cursor.execute("""INSERT INTO Department (id, name, abbr) VALUES (2, 'bleh', 'compsci')""")
            data = cursor.fetchall()[0] #list(cursor)
            
            p = "SELECT * from Tag"
            cursor.execute(p)
            data2 = cursor.fetchall()
            
            r = "SELECT * from Attribute"
            cursor.execute(r)
            data3 = cursor.fetchall()
            
            s = "SELECT id, name from Professor"
            cursor.execute(s)
            data4 = cursor.fetchall()
            
            return render_template('rate-class.html', course=data, tags=data2, course_attributes=data3, profs=data4)
#             if len(data) is 0:
#                 conn.commit()
#                 return json.dumps({'error1': 'no matching data'})
#             else:
#                 return json.dumps({'message':str(data[0])})
#         else:
#             return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error2':str(e)})

@app.route("/submit_rating/<int:course>", methods=['POST', 'GET'])
def submit_rating(course):
    try:
        # read the posted values from the UI
        _tags = request.form.getlist('tag')
        _semester = request.form.getlist('semester')[0]
        _year = request.form.get('year')
        _prof = request.form.get('prof')
        
        # validate the received values
        if _tags:
            conn = connect_to_cloudsql()
            cursor = conn.cursor()
            
            q = "SELECT id FROM Class WHERE course = %s and teacher = %s" 
            cursor.execute(q, (str(course), _prof))
            data = cursor.fetchall()
             
            if len(data) == 0:
                p = "INSERT INTO Class(course, teacher) VALUES (%s, %s)"
                cursor.execute(p, (str(course), _prof))
                t = "SELECT id FROM Class WHERE course = %s and teacher = %s"
                cursor.execute(t, (str(course), _prof))
                class_id = cursor.fetchall()[0]
            else:
                class_id = data[0][0]
            
                for tag in _tags:
                    r = "INSERT INTO Tag_Reviews(class_id, tag, semester, year) VALUES (%s, %s, %s, %s)"
                    cursor.execute(r, (str(class_id), str(tag), _semester, _year))
                data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return open_class(class_id)
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})

@app.route('/submit_search',methods=['POST', 'GET'])
def submit_search():
    try:
        # read the posted values from the UI
        _dept = request.form['inputClass']
        _num = request.form['num']
        _prof = request.form['prof']
        _attributes = request.form.getlist('attribute')
        _tags = request.form.getlist('tag')
        
        # validate the received values
        if _dept or _num or _prof:
            conn = connect_to_cloudsql()
            cursor = conn.cursor()
            
            conditions = []
            
            course_conditions = []
            if _dept:
                course_conditions.append("dept = (SELECT abbr FROM Department WHERE name='" + _dept + "')")
            if _num:
                course_conditions.append("num='" + _num + "'")
            if course_conditions != []:
                course_condition = "cl.course IN (SELECT id FROM Course WHERE %s)" %(" and ".join(course_conditions))
                conditions.append(course_condition)
            
            if _prof:
                prof_condition = "cl.teacher = (SELECT id FROM Professor WHERE name LIKE '%%%s%%')" %(_prof)
                conditions.append(prof_condition)
            
            classes = "SELECT cl.id AS class_id, cl.course AS course_id, cl.teacher AS prof_id FROM Class cl WHERE %s" %(" and ".join(conditions))
            q = "SELECT c1.class_id, co.dept, co.num, p.name FROM (%s) AS c1, Course co, Professor p WHERE c1.course_id = co.id AND p.id = c1.prof_id" %(classes)
            cursor.execute(q)
            data = cursor.fetchall()
            #return json.dumps({'data':data, 'query': q})
            classes = {}
            for id, dept, num, prof in data:
                tag_q = "SELECT t.name FROM Tag_Reviews r, Tag t WHERE r.class_id = %s AND t.id = r.tag" %(str(id))
                cursor.execute(tag_q)
                tag_data = cursor.fetchall()  
                print tag_data
                tags = list(set([t[0] for t in tag_data]))
                 
                attribute_q = "SELECT a.name FROM Attribute a, (SELECT attribute_id FROM Course_Attributes c WHERE c.course_id = %s) AS ai WHERE a.id = ai.attribute_id" %(str(id))
                cursor.execute(attribute_q)
                attribute_data = cursor.fetchall()  
                attributes = list(set([a[0] for a in attribute_data]))
                 
                classes[id] = (str(dept)+"-"+num, prof, attributes, tags, id)
            
            res =[]
            for key, val in classes.iteritems():
                class_attributes = val[2]
                class_tags = val[3]
                valid = True
                if _attributes:
                    for a in _attributes:
                        if a not in class_attributes:
                            valid = False
                            break
                if valid and _tags:
                    for t in _tags:
                        if t not in class_tags:
                            valid = False
                            break
                if valid:
                    res.append(val)

            conn.commit()
            return render_template('result.html', result=res)
            print "here"

        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e), 'query': q})

@app.route('/open_class/<int:c>',methods=['POST', 'GET'])
def open_class(c):
    try:
        # read the posted values from the UI
        conn = connect_to_cloudsql()
        cursor = conn.cursor()
        q = "SELECT t.u_id, name, t.anonymous, t.semester, t.year FROM Tag, (SELECT u_id, tag, anonymous, semester, year FROM Tag_Reviews WHERE class_id = %s) t WHERE t.tag = id" %(str(c)) 
        cursor.execute(q)
        data = cursor.fetchall()
        
        reviews = {}
        for user, tag, anonymous, season, year in data:
            if user not in reviews:
                reviews[user] = (anonymous, season + " " + str(year), set([]))
            anon, time, tags = reviews[user]
            tags.add(tag)
            reviews[user] = (anon, time, tags)
        conn.commit()
        return render_template("class.html", ratings=reviews)

    except Exception as e:
        return json.dumps({'error':str(e)})

if __name__ == "__main__":
    app.run()

# [END all]