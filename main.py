from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL,MySQLdb
import os
import hashlib
import json
import requests
import urllib3
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key="hahaha"

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hahaha'
app.config['MYSQL_DB'] = 'cmm'

# Intialize MySQL
mysql = MySQL(app)
USER="admin"
PASS="Pu51nt3k2019"
BASE="https://join.kemenkeu.go.id:445/api/v1/"
URL=""


def makeurl(param):
    URL=BASE+param
    return URL

@app.route("/",methods=['GET','POST'])
def login():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        #print (2)
        username=request.form['username']
        password=hashlib.md5(request.form['password'].encode("utf-8")).hexdigest()
         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('calls'))
        else:
            # Account doesnt exist or username/password incorrect
            #print(3)
            msg = 'Incorrect username/password!'
    return render_template('index.html',msg=msg)

@app.route("/logout")
def logout():
    print("haha")
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/calls")
def calls():
    ident=[]
    spacename=[]
    counter=0
    if (session['loggedin']==True):
        user=session['username']
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(makeurl("calls"), auth=(USER, PASS),verify=False)
        if(r.status_code==200):
            root = ET.fromstring(r.text)
            for x in root.findall('call'):
                ident.insert(counter,x.get('id'))
                spacename.insert(counter,x.find('name').text)
                counter=counter+1
        return render_template('calls.html',id=ident,name=spacename,count=counter,username=user)
    else:
        return redirect(url_for('login'))

@app.route("/calldetail",methods=['GET','POST'])
def calldetail():
    partname=[]
    partid=[]
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    callid=request.args.get('callid')
    callname=request.args.get('callname')
    if request.method=="POST":
        m=request.args.get('m')
        print(m)
        if (m == "1"):
            id=request.args.get('id')
            newname=request.form['newname']
            r=requests.put(makeurl("participants/"+id), {'nameLabelOverride':newname},auth=(USER, PASS),verify=False)
            print (r.status_code)
        else:
            message=request.form['message']
            duration=request.form['duration']
            position=request.form['position']
            r=requests.put(makeurl("calls/"+callid), {'messageText':message,'messagePosition':position,'messageDuration':duration},auth=(USER, PASS),verify=False)
            print (r.status_code)
    counter=0
    r = requests.get(makeurl("calls/"+callid+"/participants"), auth=(USER, PASS),verify=False)
    if(r.status_code==200):
        root = ET.fromstring(r.text)
        for x in root.findall('participant'):
            partid.insert(counter,x.get('id'))
            partname.insert(counter,x.find('name').text)
            counter=counter+1
    else:
        print ("gagal")
    return render_template('calldetails.html',id=partid,name=partname,count=counter)

@app.route("/participants")
def participants():
    id=[]
    name=[]
    callid=[]
    idcalls=[]
    spacename=[]
    callname=[]
    countercall=0
    counterpart=0
    if (session['loggedin']==True):
        user=session['username']
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(makeurl("participants"), auth=(USER, PASS),verify=False)
        y = requests.get(makeurl("calls"), auth=(USER, PASS),verify=False)
        if(r.status_code==200):
            root = ET.fromstring(r.text)
            toor = ET.fromstring(y.text)
            for x in toor.findall('call'):
                idcalls.insert(countercall,x.get('id'))
                spacename.insert(countercall,x.find('name').text)
                countercall=countercall+1
            for x in root.findall('participant'):
                id.insert(counterpart,x.get('id'))
                name.insert(counterpart,x.find('name').text)
                callid.insert(counterpart,x.find('call').text)
                counterpart=counterpart+1
            for x in range(counterpart):
                for z in range(countercall):
                    if(callid[x]==idcalls[z]):
                        callname.insert(x,spacename[z])
                    else:
                        pass


        return render_template('participants.html',id=id,name=name,count=counterpart,space=callname,spaceid=callid,username=user)
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
