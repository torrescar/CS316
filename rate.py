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
from __builtin__ import False

"""
Sample App Engine application demonstrating how to connect to Google Cloud SQL
using App Engine's native unix socket or using TCP when running locally.
For more information, see the README.md.
"""

# [START all]
from flask import Flask, render_template, request, json
from datetime import datetime
import os, re
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
    
    p = "SELECT * from Tag"
    cursor.execute(p)
    data2 = cursor.fetchall()
    return render_template('search.html', courses=data, tags=data2)

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
            q = "SELECT * from Course WHERE id = " + _class
            cursor.execute(q)
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
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for tag in _tags:
                    r = "INSERT INTO Tag_Reviews(tag_date, class_id, tag, semester, year) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(r, (timestamp, str(class_id), str(tag), _semester, _year))
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
        _tag_ids = request.form.getlist('tag')
        
        conn = connect_to_cloudsql()
        cursor = conn.cursor()
        
        _tags = []
        for tag in _tag_ids:
            tag_id_q = "SELECT name FROM Tag WHERE id=%s" %(tag)
            cursor.execute(tag_id_q)
            _tags.append(cursor.fetchall()[0][0])
          
        # validate the received values
        if _dept or _num or _prof:
            
            conditions = []
            
            course_conditions = []
            if _dept:
                course_conditions.append("dept = (SELECT id FROM Department WHERE name='" + _dept + "')")
            if _num:
                course_conditions.append("num ='" + _num + "'")
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
                
                dept_q = "SELECT abbr FROM Department where id = %s" %(dept)
                cursor.execute(dept_q)
                dept_name = cursor.fetchall()[0][0]  
                
                classes[id] = (dept_name+num, prof, attributes, tags)
            
            scores = []
            res =[]
            for key, val in classes.iteritems():
                class_attributes = val[2]
                class_tags = val[3]
                attribute_intersect = len(set(class_attributes).intersection(set(_attributes)))
                tag_intersect = len(set(class_tags).intersection(set(_tags)))
                if ((_attributes != [] and attribute_intersect > 0) or _attributes==[]) or ((_tags != [] and tag_intersect > 0) or _tags==[]):
                    score = attribute_intersect + tag_intersect
                    res.append((key, val, score))
                    scores.append((_tags, tag_intersect))
            
            res = sorted(sorted(res, key=lambda x: x[1]), key=lambda x: x[2], reverse=True)
            res = [(key, val) for key, val, score in res]

            conn.commit()
            noResults = False
            if len(res) == 0:
                noResults = True
            return render_template('result.html', result=res, noResults=noResults)

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
        q = "SELECT t.tag_date, name, t.semester, t.year FROM Tag, (SELECT tag_date, tag, semester, year FROM Tag_Reviews WHERE class_id = %s) t WHERE t.tag = id" %(str(c)) 
        cursor.execute(q)
        data = cursor.fetchall()
        
        reviews = {}
        for date, tag, season, year in data:
            if date not in reviews:
                reviews[date] = (season + " " + str(year), set([]))
            time, tags = reviews[date]
            tags.add(tag)
            reviews[date] = (time, tags)
        conn.commit()
        return render_template("class.html", ratings=reviews)

    except Exception as e:
        return json.dumps({'error':str(e)})

if __name__ == "__main__":
    app.run()

# [END all]