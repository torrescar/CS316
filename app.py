
from flask import Flask, render_template, request, json
from flask_mysqldb import MySQL

app = Flask(__name__)
mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'rmc'
app.config['MYSQL_DATABASE_DB'] = 'Class'
app.config['MYSQL_DATABASE_HOST'] = '152.3.43.158'
mysql.init_app(app)


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
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_createClass',(_dept,_num,_prof))
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