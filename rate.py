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
    conn = connect_to_cloudsql()
    cursor = conn.cursor()
    q = "SELECT abbr, Course.id, num as string, description FROM Course, Department WHERE Course.dept = Department.id"
    cursor.execute(q)
    data = cursor.fetchall()
    return render_template('rate.html', courses=data)

@app.route('/search/<int:myClass>',methods=['POST', 'GET'])
def search(myClass):
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

@app.route("/rate/<int:course>", methods=['POST', 'GET'])
def rate(course):
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
                p = "INSERT INTO Class(id, course, teacher, house, special_topics, credits) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(p, ("10", str(course), _prof, 0, 0, "1.0"))
                class_id = "10"
            else:
                class_id = data[0][0]
            
                for tag in _tags:
                    r = "INSERT INTO Tag_Reviews(u_id, class_id, tag, anonymous, semester, year) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(r, (str(0),str(class_id), str(tag), "0", _semester, _year))
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
                reviews[user] = (anonymous, season + " " + str(year), [])
            anon, time, tags = reviews[user]
            tags.append(tag)
            reviews[user] = (anon, time, tags)
        conn.commit()
        return render_template("class.html", ratings=reviews)
 
    except Exception as e:
        return json.dumps({'error':str(e)})

if __name__ == "__main__":
    app.run()

# [END all]