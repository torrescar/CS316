

from flask import Flask, render_template, request, json
import MySQLdb

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/search',methods=['POST', 'GET'])
def search():
    try:
        # read the posted values from the UI
        _dept = request.form['inputDept']
        _num = request.form['inputNum']
        _prof = request.form['inputProf']
     
        # validate the received values
        if _dept and _num and _prof:
            conn = MySQLdb.connect(unix_socket='/cloudsql/' + "master-deck-148904:us-central1:rmcinstance", db='Classes', user='root', charset='utf8')
            print "did you get here?"
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO Deptartment (id, name, abbr) VALUES (2, 'bleh', _dept)""")
            data = cursor.fetchone()
    
            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'Class created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})

if __name__ == "__main__":
    app.run()