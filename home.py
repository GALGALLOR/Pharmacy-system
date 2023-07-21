from flask_mysqldb import MySQL
from flask import  get_flashed_messages, session,Flask,render_template,redirect,request,flash,url_for
app=Flask(__name__)
import datetime


mydb=MySQL(app)

"""app.config['MYSQL_HOST']=''
app.config['MYSQL_USER']=''
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']=''"""

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='GALGALLO10'
app.config['MYSQL_DB']='PHARMACY_BORU'

app.secret_key='mimi'

@app.route('/')
def home():
    return redirect(url_for('signin'))

@app.route('/sign_in',methods=["GET","POST"])
def signin():
    if request.method=='POST':
        try:
            #check if the user has input something
            fullname = str(request.form["fullname"])
            id_number= int(request.form['id'])
        except:
            #pass if the user submitted blank
            pass
        #check if it is in database
        try:
            cursor=mydb.connection.cursor()
            cursor.execute(f'SELECT FULL_NAME FROM USERS WHERE ID_NUMBER="{id_number}"')
            identity=cursor.fetchall()[0][0]
            print(identity)

            #checkin time
            checkin_time=datetime.datetime.now().strftime('%H%M00')
            date=datetime.datetime.now().strftime("%Y-%m-%d")
            print(date)

            cursor=mydb.connection.cursor()
            cursor.execute('INSERT INTO WORKLOG(ID_NUMBER,FULLNAME,CHECKIN_TIME,DATE)VALUES(%s,%s,%s,%s)',(id_number,fullname,checkin_time,date))
            mydb.connection.commit()

            session['fullname']=fullname

            return redirect(url_for('order'))
        
        except:
            msg = 'the user does not exist'
            print(msg)
            return render_template('signin.html',msg=msg)

        
    else:
        if 'fullname' in session:
            session.pop('fullname', None)
            print("You have been logged out successfully!")
        return render_template('signin.html')

@app.route('/order' ,methods=['POST','GET'] )
def order():
    if 'fullname' in session:
        fullname=session['fullname']
        if request.method=='POST':
            submit=str(request.form['submit'])
        
        else:
            #list down the drugs
            cursor=mydb.connection.cursor()
            cursor.execute(f'SELECT * FROM STOCK')
            alldrugs=cursor.fetchall()

    else:
        return redirect(url_for('signin'))
    return render_template('order2.html')

if __name__ == '__main__':
    app.run(debug=True)