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
    if 'fullname' in session:
        return redirect(url_for('order'))
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
            cursor.execute(f'SELECT TWO_NAMES FROM USERS WHERE USER_ID="{id_number}"')
            identity=cursor.fetchall()[0][0]
            print(identity)

            #checkin time
            '''checkin_time=datetime.datetime.now().strftime('%H%M00')
            date=datetime.datetime.now().strftime("%Y-%m-%d")
            print(date)

            cursor=mydb.connection.cursor()
            cursor.execute('INSERT INTO WORKLOG(ID_NUMBER,TWO_NAMES,CHECKIN_TIME,DATE)VALUES(%s,%s,%s,%s)',(id_number,fullname,checkin_time,date))
            mydb.connection.commit()'''

            session['fullname']=fullname
            session['id']=id_number

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

            cursor=mydb.connection.cursor()
            cursor.execute('SELECT * from STOCK_TABLE')
            counter=cursor.fetchall()
            Sold_items=[]
            for num in counter:
                sold_item=[]
                sold_item.append(num[0])
                sold_item.append(str(request.form[str(num[0])]))
                Sold_items.append(sold_item)
                #stockID,Quantity
            #update sales_table,rem_stock in stock,transaction,transaction_items
            
            #Get last Transaction_id
            cursor=mydb.connection.cursor()
            cursor.execute('SELECT TRANSACTION_ID FROM TRANSACTION')
            last_transaction_id=cursor.fetchall()[-1][0]
            last_transaction_id=int(last_transaction_id)+1
            #Get last Sales_ID
            cursor=mydb.connection.cursor()
            cursor.execute('SELECT SALES_ID FROM SALES')
            last_sales_id=cursor.fetchall()[-1][0]
            last_sales_id=int(last_sales_id)+1
            sale_date=str(datetime.date.today())
            total_cost=0
            #Get Product cost for each ID
            for stockID in Sold_items:
                if int(stockID[1])==0:
                    pass
                else:
                    cursor=mydb.connection.cursor()
                    cursor.execute('SELECT PRODUCT_ID FROM STOCK_TABLE WHERE STOCK_ID='+str(stockID[0]))
                    prod_id=cursor.fetchall()[0][0]
                    cursor=mydb.connection.cursor()
                    cursor.execute('SELECT * FROM DRUG_DETAILS WHERE DRUG_ID='+str(prod_id))
                    cost_drug_name=cursor.fetchall()
                    cost=cost_drug_name[0][7]
                    drug_name=cost_drug_name[0][1]
                    #Get subtotal
                    subtotal=int(cost)*int(stockID[1])
                    total_cost=total_cost+int(subtotal)
                    #Add to Transaction_Items
                    #Get last Transaction_item_id
                    cursor=mydb.connection.cursor()
                    cursor.execute('SELECT TRANSACTION_ITEM_ID FROM TRANSACTION_ITEMS')
                    last_Titem_id=cursor.fetchall()[-1][0]
                    print(last_Titem_id)
                    last_Titem_id=int(last_Titem_id)+1
                    #insert into Transaction_item_id
                    cursor.execute('INSERT INTO TRANSACTION_ITEMS(TRANSACTION_ITEM_ID,TRANSACTION_ID,QUANTITY,UNIT_PRICE,PRODUCT_NAME,SUBTOTAL)VALUES(%s,%s,%s,%s,%s,%s)',(last_Titem_id,last_transaction_id,stockID[1],cost,drug_name,subtotal))
                    mydb.connection.commit()
                    #insert into SALES
                    cursor.execute('INSERT INTO SALES(SALES_ID,PRODUCT_ID,SALES)')
                    mydb.connection.commit()

            #insert transaction
            
            id_number=str(session['id'])
            cursor.execute('INSERT INTO TRANSACTION(TRANSACTION_ID,CASHIER_ID,SALE_DATE,TOTAL_SALES)VALUES(%s,%s,%s,%s)',(last_transaction_id,id_number,sale_date,total_cost))
            mydb.connection.commit()
            #Deduct from the inventory
            #deduct from stocks_table[rem_stock]
            
            

        else:
            pass            
                        

    else:
        return redirect(url_for('signin'))
    
    #list down past transactions
    cursor=mydb.connection.cursor()
    cursor.execute('SELECT * FROM TRANSACTION')
    past_transactions=cursor.fetchall()
    cursor.execute('SELECT * FROM TRANSACTION_ITEMS')
    past_transaction_items=cursor.fetchall()
    #list Down DrugDetails,inventory & stock
    cursor.execute('SELECT * FROM DRUG_DETAILS')
    drug_details=cursor.fetchall()
    cursor.execute('SELECT QUANTITY FROM INVENTORY')
    inventory=cursor.fetchall()
    cursor.execute('SELECT * FROM STOCK_TABLE')
    stocks=cursor.fetchall()
    return render_template('order2.html',stocks=stocks,drug_details=drug_details, past_transaction_items=past_transaction_items,past_transactions=past_transactions)

if __name__ == '__main__':
    app.run(debug=True)