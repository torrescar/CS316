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
    q = "SELECT dept, id, num, description FROM Course, "
    cursor.execute(q)
    data = cursor.fetchall()
    return render_template('rate.html', courses=data)

@app.route('/search',methods=['POST', 'GET'])
def search():
    try:
        # read the posted values from the UI
        _class = str(request.form['hiddenInputClass'])
        # validate the received values
        if True:
            conn = connect_to_cloudsql()
            cursor = conn.cursor()
            #cursor.execute("SELECT * FROM Department")
            q = "SELECT * from Course WHERE id = %s"
            cursor.execute(q, (_class))
            #cursor.execute("""INSERT INTO Department (id, name, abbr) VALUES (2, 'bleh', 'compsci')""")
            data = list(cursor)

            if len(data) is 0:
                conn.commit()
                return json.dumps({'error1': 'no matching data'})
            else:
                return json.dumps({'message':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error2':str(e)})

if __name__ == "__main__":
    app.run()

# [END all]

