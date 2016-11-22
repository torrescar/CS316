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
    return render_template('index.html')

@app.route('/search',methods=['POST', 'GET'])
def search():
    try:
        # read the posted values from the UI
        _dept = request.form['dept']
        _num = request.form['num']
        _prof = request.form['prof']
        _attributes = request.form.getlist('attribute')
        
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
                course_condition = "cl.course = (SELECT id FROM Course WHERE %s)" %(" and ".join(course_conditions))
                conditions.append(course_condition)
            
            if _prof:
                prof_condition = "cl.teacher = (SELECT id FROM Professor WHERE name LIKE '%s%')" %(_prof)
                conditions.append(prof_condition)
            
            classes = "SELECT cl.id AS class_id, cl.course AS course_id, cl.teacher AS prof_id FROM Class cl WHERE %s" %(" and ".join(conditions))
            q = "SELECT c1.class_id, co.dept, co.num, p.name FROM (%s) c1, Course co, Professor p WHERE c1.course_id = co.id AND p.id = c1.prof_id" %(classes)
            cursor.execute(q)
            data = cursor.fetchall()
            return json.dumps({'data':data})
            
            classes = {}
            for id, dept, num, prof in data:
                tag_q = "SELECT tag FROM Tag_Review t WHERE t.class_id = %s" %(str(id))
                cursor.execute(tag_q)
                tag_data = cursor.fetchall()  
                tags = [t[0] for t in tag_data]
                
                attribute_q = "SELECT a.name FROM Attribute a, (SELECT attribute_id FROM Course_Attributes c WHERE c.course_id = %s) WHERE a.id = attribute_id" %(str(id))
                cursor.execute(attribute_q)
                attribute_data = cursor.fetchall()  
                attributes = [a[0] for a in attribute_data]
                
                classes[id] = (dept+num, prof, attributes, tags)
                

            if len(data) > 0:
                conn.commit()
                return render_template('result.html', result=data)
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})

if __name__ == "__main__":
    app.run()

# [END all]
