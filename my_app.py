

from flask import Flask, render_template, request, json
import MySQLdb

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('my_index.html')

@app.route("/showSearch",methods=['GET'])
def showSearch():
    return render_template('index.html')

@app.route("/showRate",methods=['POST', 'GET'])
def showRate():
    #return render_template('rate.html')
    pass

@app.route('/search',methods=['POST', 'GET'])
def search():
    try:
        # read the posted values from the UI
        _dept = request.form['inputDept']
        _num = request.form['inputNum']
        _prof = request.form['inputProf']

        # validate the received values
        if _dept and _num and _prof:
            conn = MySQLdb.connect("104.198.135.7", "root", "rmcinstance", db="Classes")
            print "did you get here?"
            cursor = conn.cursor()
            #cursor.execute("SELECT * FROM Department")
            q = "INSERT INTO Department(id, name, abbr) VALUES (%s, %s, %s)"
            cursor.execute(q, (2,'computerscience','cs'))
            #cursor.execute("""INSERT INTO Department (id, name, abbr) VALUES (2, 'bleh', 'compsci')""")
            data = cursor.fetchall()

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