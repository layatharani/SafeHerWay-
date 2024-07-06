# main.py
import base64
import calendar
import csv
import datetime
import hashlib
import io
import math
import os
import random
import shutil
import subprocess
import urllib.parse
import urllib.request
import webbrowser
from random import randint
from urllib.request import urlopen

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd
import seaborn as sns
from flask import (Flask, Response, abort, redirect, render_template, request,
                   session, url_for)
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  charset="utf8",
  database="crime_hotspot_new"

)
app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
#######
UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = { 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####
@app.route('/', methods=['GET', 'POST'])
def index():
    msg=""
    if request.method=='POST':
        uname=request.form['email']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM ch_register WHERE email = %s AND pass = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            ff=open("static/user.txt","w")
            ff.write(uname)
            ff.close()
            
            return redirect(url_for('view_map'))
        else:
            msg = 'Incorrect username/password!'
    #shutil.copy("static/dataset/mydata.html","templates/myroute1.html")

    #txt='<input type="text" id="t1" name="t1" value="Srirangam, Trichy">'
    #ff=open("templates/myroute1.html","a")
    #ff.write(txt)
    #ff.close()

    
    '''mycursor = mydb.cursor()
    df=pd.read_csv('static/dataset/crime_area.csv')
    df.head()
    
    for ds in df.values:
        mycursor.execute("SELECT max(id)+1 FROM ch_area")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        lc=ds[3]
        lo=lc.split(",")
        lat=lo[0]
        lon=lo[1]
        
        sql = "INSERT INTO ch_area(id,district,crime,area,lat,lon) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid,ds[0],ds[1],ds[2],lat,lon)
        mycursor.execute(sql, val)
        mydb.commit()'''
        
        
    return render_template('web/index.html',msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('admin'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('web/login.html',msg=msg)



@app.route('/register', methods=['GET', 'POST'])
def register():
    
    msg=""
    if request.method=='POST':
        name=request.form['name']
        
        email=request.form['email']
        
        pass1=request.form['pass']
        
        
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM ch_register where email=%s",(email,))
        cnt = mycursor.fetchone()[0]
        
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM ch_register")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
                    
            sql = "INSERT INTO ch_register(id,name,email,pass) VALUES (%s, %s, %s, %s)"
            val = (maxid,name,email,pass1)
            mycursor.execute(sql, val)
            mydb.commit()            
            #print(mycursor.rowcount, "Registered Success")
            msg="success"
            
        else:
            msg='fail'

            
    return render_template('web/register.html',msg=msg)
# safety percentage code 
def read_crime_data(filename):
    crime_data = {}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            place = row['places']
            crime_data[place] = float(row['totalcrime'])
    return crime_data

# Function to categorize safety level
def categorize_safety(safety_percentage):
    if safety_percentage >= 75:
        return 'Safety'
    elif safety_percentage >= 50:
        return 'Medium'
    else:
        return 'Danger'

# Route for the index page
@app.route('/safety')
def safety():
    return render_template('safety.html')

# Route to handle safety percentage calculation
@app.route('/calculate_safety', methods=['POST'])
def calculate_safety():
    source = request.form['source']
    destination = request.form['destination']
    
    crime_data = read_crime_data('static/dataset/dataset.csv')  # Change filename here
    
    if source in crime_data and destination in crime_data:
        crime_rate_source = crime_data[source]
        crime_rate_destination = crime_data[destination]
        total_crime=crime_rate_source+crime_rate_destination
        safety_percentage = ((500-total_crime) /500) *100
        
        # Categorize safety level
        safety_level = categorize_safety(safety_percentage)
        
        return render_template('safetyresult.html', 
                               safety_percentage=safety_percentage,
                               safety_level=safety_level)
    else:
        return "Invalid source or destination"


def unique(list1):
 
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    #for x in unique_list:
    #    print x,
    return unique_list


'''@app.route('/add_crime', methods=['GET', 'POST'])
def add_crime():
    msg=""
    district=""
    year=""
    year1=0
    st=""
    act=request.args.get("act")
    df=pd.read_csv('static/dataset/crimefile.csv')
    df.head()
    #if not "TOAL" in ds[2]:
    dst=[]
    dyt=[]
    cr=[]
    for ds in df.values:
        if ds[2]=="TOTAL" or ds[2]=="ZZ TOTAL" or ds[2]=="Cyber Cell" or ds[2]=="Other Units" or ds[2]=="Total District(s)":
            s=1
        else:
            dst.append(ds[2])
            dyt.append(ds[3])

    r_district=unique(dst)
    r_year=unique(dyt)
    if request.method=='POST':
        st="1"
        district=request.form['district']
        year=request.form['year']
        year1=int(year)

        for ds in df.values:
            if ds[2]==district and ds[3]==year1:
                cr.append(ds[4])
                cr.append(ds[5])
                cr.append(ds[6])
                cr.append(ds[7])
                cr.append(ds[8])
                cr.append(ds[9])
                

        
    print(cr)
        
    return render_template('add_crime.html',msg=msg,act=act,r_district=r_district,r_year=r_year,district=district,year1=year1,cr=cr,st=st)


@app.route('/add_area', methods=['GET', 'POST'])
def add_area():
    msg=""
    district=request.args.get("district")
    crime=request.args.get("crime")
    num_crime=request.args.get("num_crime")
    year=""
    year1=0
    sdata=[]
    data=[]
    st=""
    act=request.args.get("act")
    mycursor = mydb.cursor()
    
    df=pd.read_csv('static/dataset/crimefile.csv')
    df.head()
    #if not "TOAL" in ds[2]:
    dst=[]
    dyt=[]
    cr=[]
    for ds in df.values:
        if ds[2]=="TOTAL" or ds[2]=="ZZ TOTAL" or ds[2]=="Cyber Cell" or ds[2]=="Other Units" or ds[2]=="Total District(s)":
            s=1
        else:
            dst.append(ds[2])
            dyt.append(ds[3])

    r_district=unique(dst)
    r_year=unique(dyt)
    
    if request.method=='POST':
        st="1"
        district=request.form['district']
        crime=request.form['crime']
        num_crime=request.form['num_crime']
        t1=request.form['t1']
        

        if t1=="1":
            nn=int(num_crime)

            i=1
            while i<=nn:
                sdata.append(str(i))
                i+=1

        if t1=="2":
            area=request.form.getlist("area[]")
            loc=request.form.getlist("loc[]")

            #print(area)
            ln=len(area)
            j=0
            for area1 in area:
                mycursor.execute("SELECT max(id)+1 FROM ch_area")
                maxid = mycursor.fetchone()[0]
                if maxid is None:
                    maxid=1

                lc=loc[j]
                lo=lc.split(",")
                lat=lo[0]
                lon=lo[1]
                
                sql = "INSERT INTO ch_area(id,district,crime,area,lat,lon) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (maxid,district,crime,area1,lat,lon)
                mycursor.execute(sql, val)
                mydb.commit()

                j+=1
            msg="ok"

        mycursor.execute("SELECT * FROM ch_area where district=%s && crime=%s",(district,crime))
        data = mycursor.fetchall()
    

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from ch_area where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_area',district=district,crime=crime,num_crime=num_crime))
        
       
    
    return render_template('add_area.html',msg=msg,act=act,r_district=r_district,r_year=r_year,district=district,crime=crime,num_crime=num_crime,sdata=sdata,st=st,data=data)'''


@app.route('/add_area', methods=['GET', 'POST'])
def add_area():
    msg=""
    latt=13.083551;
    lonn=80.193957;
    district=""
    data=[]
    st=""
    act=request.args.get("act")
    mycursor = mydb.cursor()

    
    
    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    r_district.sort()
    
    
    if request.method=='POST':
        st="1"
        district=request.form['district']
        if district=="":
            s=1
        else:
            for ds1 in df.values:
                if ds1[5]==district:
                    latt=ds1[8]
                    lonn=ds1[9]
                    
  
       
    
    return render_template('add_area.html',msg=msg,act=act,r_district=r_district,district=district,latt=latt,lonn=lonn)

@app.route('/map_push2', methods=['GET', 'POST'])
def map_push2():
    msg=""
    latt=request.args.get("latt")
    lonn=request.args.get("lonn")
    sdata=[]
    district=request.args.get("district")
   
    mycursor = mydb.cursor()
    
   
        
    if request.method=='POST':
        st="1"
        area=request.form["area"]
        pincode=request.form["pincode"]
        t1=request.form["t1"]
        t11=t1.split("),")

        t2=t11[0].split("(")
        loc=t2[1]
        #lc=loc[j]
        lo=loc.split(",")
        lat=lo[0]
        lon=lo[1]
        insdata=['IN',pincode,area,'Tamil Nadu','25',district,'616','z',lat,lon,'3','y']

        with open('static/dataset/crime_postal.csv','a',newline='') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(insdata)
        
        msg="ok"

    return render_template('map_push2.html',msg=msg,latt=latt,lonn=lonn,district=district)




@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    msg=""
    latt=13.083551;
    lonn=80.193957;
    district=request.args.get("district")
    area=request.args.get("area")
    pincode=request.args.get("pincode")
    crime=request.args.get("crime")
    year=request.args.get("year")
    num_crime=request.args.get("num_crime")
    if num_crime is None:
        num_crime="2"
    r_area=[]
    sdata=[]
    data=[]
    st=""
    act=request.args.get("act")
    mycursor = mydb.cursor()
    ##
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    y1=now.strftime("%Y")
    y11=int(y1)-1
    ydata=[]
    h=0
    while h<4:
        ydata.append(str(y11))
        y11-=1
        
        h+=1
    ##
    
    
    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    r_district.sort()
    
    
    if request.method=='POST':
        st="1"
        
        district=request.form['district']
        if district=="":
            s=1
        else:
            for ds1 in df.values:
                if ds1[5]==district:
                    dyt.append(ds1[2])

            r_area=unique(dyt)
            r_area.sort()

            area=request.form['area']

            for ds2 in df.values:
                if ds2[5]==district and ds2[2]==area:
                    latt=ds2[8]
                    lonn=ds2[9]
                    pincode=ds2[1]
            crime=request.form['crime']
            year=request.form['year']
            num_crime=request.form['num_crime']
       
    
    return render_template('add_location.html',msg=msg,act=act,ydata=ydata,r_district=r_district,district=district,r_area=r_area,area=area,pincode=pincode,crime=crime,year=year,num_crime=num_crime,latt=latt,lonn=lonn)


@app.route('/map_push', methods=['GET', 'POST'])
def map_push():
    msg=""
    latt=request.args.get("latt")
    lonn=request.args.get("lonn")
    sdata=[]
    district=request.args.get("district")
    crime=request.args.get("crime")
    area=request.args.get("area")
    year=request.args.get("year")
    pincode=request.args.get("pincode")
    num_crime=request.args.get("num_crime")

    mycursor = mydb.cursor()
    
    
    if num_crime is None:
        num_crime="2"
        
    nn=int(num_crime)

    i=1
    while i<=nn:
        sdata.append(str(i))
        i+=1
        
    if request.method=='POST':
        st="1"
        address=request.form.getlist("address[]")
        t1=request.form["t1"]

        #print(area)
        ln=len(area)
        j=0

        t11=t1.split("),")
        
        nn=int(num_crime)
        while j<nn:
            mycursor.execute("SELECT max(id)+1 FROM ch_location")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            t2=t11[j].split("(")
            loc=t2[1]
            #lc=loc[j]
            lo=loc.split(",")
            lat=lo[0]
            lon=lo[1]
            
            sql = "INSERT INTO ch_location(id,district,crime,area,lat,lon,address,pincode,year) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)"
            val = (maxid,district,crime,area,lat,lon,address[j],pincode,year)
            mycursor.execute(sql, val)
            mydb.commit()

            j+=1
        msg="ok"

    return render_template('map_push.html',msg=msg,latt=latt,lonn=lonn,num_crime=num_crime,district=district,area=area,pincode=pincode,crime=crime,year=year,sdata=sdata)

@app.route('/view_map', methods=['GET', 'POST'])
def view_map():
    msg=""
    uname=""
    district=""
    year=""
    year1=0
    data3=[]
    hdata=[]
    sdata=[]
    st=""
    act=request.args.get("act")
    #if 'username' in session:
    #    uname = session['username']
    ff=open("static/user.txt","r")
    user=ff.read()
    ff.close()
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ch_register where email=%s",(user,))
    usr = mycursor.fetchone()
    name=usr[1]

    mycursor = mydb.cursor()

    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()
    #if not "TOAL" in ds[2]:
    dst=[]
    dyt=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
    

    r_district=unique(dst)
    r_district.sort()

    if request.method=='POST':
        st="1"

        mycursor.execute("delete from ch_temp")
        mydb.commit()
                    
        district=request.form['district']
        mycursor.execute("SELECT * FROM ch_location where district=%s",(district,))
        value = mycursor.fetchall()

        df=pd.read_csv('static/dataset/crime_postal.csv')
        j=0
        
        for d2 in df.values:
            dt=[]
            cnt=0
            if d2[5]==district:

                area=d2[2]
                mycursor.execute("SELECT count(*) FROM ch_location where district=%s && area=%s",(district,area))
                cnt = mycursor.fetchone()[0]
                
                dt.append(d2[2])
                dt.append(d2[1])
                dt.append(str(cnt))
                if cnt>0:
                    #docs2.append(d2[2])
                    #values2.append(cnt)
                    
                    
                    mycursor.execute("SELECT max(id)+1 FROM ch_temp")
                    maxid = mycursor.fetchone()[0]
                    if maxid is None:
                        maxid=1
                    sql = "INSERT INTO ch_temp(id,area,scount) VALUES (%s, %s, %s)"
                    val = (maxid,d2[2],cnt)
                    mycursor.execute(sql, val)
                    mydb.commit()
                
                data3.append(dt)

        data3.sort()
        ####
        doc=[]
        values=[]
        mycursor.execute("SELECT count(*),year FROM ch_location where district=%s group by year",(district,))
        value1 = mycursor.fetchall()
        for vv1 in value1:
            
            doc.append(vv1[1])
            values.append(vv1[0])
        #graph1   
        #dd2=val

        
        mx=max(values)
        g1=mx+2
        #ax=dd2
        #dd1=datah

        #doc = dd1 #list(data.keys())
        #values = dd2 #list(data.values())
          
        fig = plt.figure(figsize = (10, 5))

        #c=['green','orange','yellow','red']
        colors = ['#a9f971', '#fdaa48','#6890F0','#A890F0']
        # creating the bar plot
        plt.bar(doc, values, color=colors, width = 0.4)

        plt.ylim((1,g1))

        plt.xlabel("Year")
        plt.ylabel("Number of Crimes")
        plt.title("")


        fn="graph1.png"
        plt.xticks(rotation=0)

        plt.savefig('static/'+fn)
        plt.close()
        ####################################
        
        docs2=[]
        values2=[]
        gdata=[]
        mycursor.execute("SELECT * from ch_temp order by scount desc limit 0,12")
        fdata = mycursor.fetchall()
        for fd in fdata:
            gt=[]
            at=[]
            docs2.append(fd[1])
            values2.append(fd[2])
            #print(fd[1])
            a1=0
            a2=0
            a3=0
            a4=0
            a5=0
            a6=0
            
            mycursor.execute("SELECT * from ch_location where area=%s",(fd[1],))
            adata = mycursor.fetchall()
            
            for ad in adata:
                if ad[2]=="Rape":
                    a1+=1
                    
                if ad[2]=="Kidnapping and Abduction":
                    a2+=1
                    
                if ad[2]=="Dowry Deaths":
                    a3+=1
                    
                if ad[2]=="Assault on women with intent to outrage her modesty":
                    a4+=1
                    
                if ad[2]=="Insult to modesty of Women":
                    a5+=1
                    
                if ad[2]=="Cruelty by Husband or his Relatives":
                    a6+=1
            if a1>0:
                at.append(a1)
            else:
                at.append(0)
            if a2>0:
                at.append(a2)
            else:
                at.append(0)

            if a3>0:
                at.append(a3)
            else:
                at.append(0)

            if a4>0:
                at.append(a4)
            else:
                at.append(0)

            if a5>0:
                at.append(a5)
            else:
                at.append(0)

            if a6>0:
                at.append(a6)
            else:
                at.append(0)
                
            gt.append(fd[1])
            gt.append(at)
            gdata.append(gt)
            
            
        #ax=dd2
        #dd1=datah
        mx=max(values2)
        g2=mx+2
        #doc = dd1 #list(data.keys())
        #values = dd2 #list(data.values())
          
        fig = plt.figure(figsize = (10, 8))

        c=['#990000','#FF0000','#FF6600','#996600','#CC0066','#FFFF33','#006699','#0066CC','#666699','#006666','#669966','#009933']
        # creating the bar plot
        plt.bar(docs2, values2, color=c, width = 0.4)

        plt.ylim((1,g2))

        plt.xlabel("Area")
        plt.ylabel("Number of Crimes")
        plt.title("")


        fn="graph2.png"
        plt.xticks(rotation=20)

        plt.savefig('static/'+fn)
        plt.close()
        ##################################
        
        j=1
        for gdd in gdata:
            
            docs3=['a','b','c','d','e','f']
            mx=max(gdd[1])
            g2=mx+2
            #doc = dd1 #list(data.keys())
            #values = dd2 #list(data.values())
              
            fig = plt.figure(figsize = (6, 4))

            c=['orange','red','pink','yellow','blue','brown']
            # creating the bar plot
            plt.bar(docs3, gdd[1], color=c, width = 0.4)
            
            plt.ylim((1,g2))

            plt.xlabel("Crime")
            plt.ylabel("Number of Crimes")
            plt.title(gdd[0],fontsize=14)


            fn="g"+str(j)+".png"
            plt.xticks(rotation=0)

            plt.savefig('static/'+fn)
            plt.close()
            j+=1
        ################################
        
        mycursor.execute("SELECT * FROM ch_temp order by scount desc")
        mv = mycursor.fetchall()
        mval=mv[0][2]
        print(mval)

        n1=mval/2
        #50
        n11=math.floor(n1)
        n2=n11/2
        #25
        n22=math.floor(n2)
        print(n22)
        #75
        n33=n11+n22
        
        
        for d3 in df.values:
            dt=[]
            cnt=0
            if d3[5]==district:

                area=d3[2]
                mycursor.execute("SELECT count(*) FROM ch_location where district=%s && area=%s",(district,area))
                cnt = mycursor.fetchone()[0]
                if cnt>0:
                    v=d3[2]+" ("+str(cnt)+")"
                    hdata.append(v)
                else:
                    sdata.append(d3[2])

        hdata.sort()
        sdata.sort()
        #################
        
    return render_template('view_map.html',msg=msg,act=act,name=name,r_district=r_district,district=district,st=st,data3=data3,hdata=hdata,sdata=sdata)


@app.route('/map', methods=['GET', 'POST'])
def map():
    msg=""
    district=request.args.get("district")
    data=[]
    data1=[]
    data2=[]
    data3=[]
    data4=[]
    data5=[]
    data6=[]
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ch_location where district=%s",(district,))
    value = mycursor.fetchall()

    latt=value[0][4]
    lonn=value[0][5]
    
    #df=pd.read_csv('static/dataset/crime_area.csv')

    '''for d1 in value:
        dt=[]
        #if d1[0]==district:
        #loc=d1[3].split(",")
        dt.append(d1[3])
        dt.append(d1[4])
        dt.append(d1[5])
        dt.append(d1[6])
        dt.append(d1[7])
        dt.append(d1[2])
        data.append(dt)
            
    ####SAFE######

    df=pd.read_csv('static/dataset/crime_postal.csv')
    j=0
    for d2 in df.values:
        dt=[]
        if d2[5]==district:
            area=d2[2]
            mycursor.execute("SELECT count(*) FROM ch_location where district=%s && area=%s",(district,area))
            cnt = mycursor.fetchone()[0]

            if cnt<=3:
                if j<200:
                    #print(area)
                    dt.append(d2[2])
                    dt.append(d2[5])
                    dt.append(d2[1])
                    dt.append(d2[8])
                    dt.append(d2[9])
                    data3.append(dt)
                j+=1'''
            
    ###Report###
    df=pd.read_csv('static/dataset/crime_postal.csv')
    mycursor.execute("SELECT * FROM ch_temp order by scount desc")
    mv = mycursor.fetchall()
    mval=mv[0][2]
    #print(mval)

    n1=mval/2
    #50
    n11=math.floor(n1)
    n2=n11/2
    #25
    n22=math.floor(n2)
    #print(n22)
    #75
    n33=n11+n22
    ar1=[]
    
    
    for d1 in df.values:
        dt=[]
        dt1=[]
        cnt=0
        if d1[5]==district:
    
           
            area=d1[2]
            mycursor.execute("SELECT count(*) FROM ch_location where district=%s && area=%s",(district,area))
            cnt = mycursor.fetchone()[0]
            if cnt>0:
                ar1.append(area)

    ar2=unique(ar1)
    print(ar2)
    j=0
    for ar22 in ar2:
        for d2 in df.values:
            if d2[5]==district and d2[2]==ar22:
                dt=[]
                dt.append(d2[2])
                dt.append(d2[8])
                dt.append(d2[9])
                dt.append(d2[5])
                dt.append(d2[1])
                data.append(dt)

                mycursor.execute("SELECT * FROM ch_location where district=%s && area=%s && status=0",(district,ar22))
                rw1 = mycursor.fetchall()

                dt1=[]
                dt2=[]
                dt3=[]
                dt4=[]
                dt5=[]
                dt6=[]
                for rw11 in rw1:
                    if rw11[2]=="Rape":
                        dt1.append(rw11[3])
                        dt1.append(rw11[4])
                        dt1.append(rw11[5])
                        dt1.append(rw11[1])
                        dt1.append(rw11[7])
                        dt1.append(rw11[6])
                        dt1.append(rw11[2])
                        data1.append(dt1)
                    if rw11[2]=="Kidnapping and Abduction":
                        dt2.append(rw11[3])
                        dt2.append(rw11[4])
                        dt2.append(rw11[5])
                        dt2.append(rw11[1])
                        dt2.append(rw11[7])
                        dt2.append(rw11[6])
                        dt2.append(rw11[2])
                        data2.append(dt2)
                    if rw11[2]=="Dowry Deaths":
                        dt3.append(rw11[3])
                        dt3.append(rw11[4])
                        dt3.append(rw11[5])
                        dt3.append(rw11[1])
                        dt3.append(rw11[7])
                        dt3.append(rw11[6])
                        dt3.append(rw11[2])
                        data3.append(dt3)
                    if rw11[2]=="Assault on women with intent to outrage her modesty":
                        dt4.append(rw11[3])
                        dt4.append(rw11[4])
                        dt4.append(rw11[5])
                        dt4.append(rw11[1])
                        dt4.append(rw11[7])
                        dt4.append(rw11[6])
                        dt4.append(rw11[2])
                        data4.append(dt4)
                    if rw11[2]=="Insult to modesty of Women":
                        dt5.append(rw11[3])
                        dt5.append(rw11[4])
                        dt5.append(rw11[5])
                        dt5.append(rw11[1])
                        dt5.append(rw11[7])
                        dt5.append(rw11[6])
                        dt5.append(rw11[2])
                        data5.append(dt5)
                    if rw11[2]=="Cruelty by Husband or his Relatives":
                        dt6.append(rw11[3])
                        dt6.append(rw11[4])
                        dt6.append(rw11[5])
                        dt6.append(rw11[1])
                        dt6.append(rw11[7])
                        dt6.append(rw11[6])
                        dt6.append(rw11[2])
                        data6.append(dt6)
                        
            
            j+=1


    
    return render_template('map.html',msg=msg,data=data,data1=data1,data2=data2,data3=data3,data4=data4,data5=data5,data6=data6,district=district,latt=latt,lonn=lonn)

@app.route('/map2', methods=['GET', 'POST'])
def map2():
    msg=""
    district=request.args.get("district")
    data=[]
    data2=[]
    data3=[]
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ch_location where district=%s",(district,))
    value = mycursor.fetchall()

    latt=value[0][4]
    lonn=value[0][5]
    
    #df=pd.read_csv('static/dataset/crime_area.csv')

    for d1 in value:
        dt=[]
        #if d1[0]==district:
        #loc=d1[3].split(",")
        dt.append(d1[3])
        dt.append(d1[4])
        dt.append(d1[5])
        dt.append(d1[6])
        dt.append(d1[7])
        dt.append(d1[2])
        data.append(dt)
                
    return render_template('map2.html',msg=msg,data=data,data2=data2,data3=data3,district=district,latt=latt,lonn=lonn)


@app.route('/view_route', methods=['GET', 'POST'])
def view_route():
    msg=""
    uname=""
    district=""
    r_area=[]
    r_area2=[]
    area=""
    area2=""
    data=[]
    
    st=""
    act=request.args.get("act")
    #if 'username' in session:
    #    uname = session['username']
    mycursor = mydb.cursor()
    ff=open("static/user.txt","r")
    user=ff.read()
    ff.close()
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ch_register where email=%s",(user,))
    usr = mycursor.fetchone()
    name=usr[1]
    
    
    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    dyt2=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    r_district.sort()
    
    
    if request.method=='POST':
        st="1"
        
        district=request.form['district']
        if district=="":
            s=1
        else:
            for ds1 in df.values:
                if ds1[5]==district:
                    dyt.append(ds1[2])
                    dyt2.append(ds1[2])

            r_area=unique(dyt)
            r_area2=unique(dyt2)

            r_area.sort()
            r_area2.sort()

            area=request.form['area']
            area2=request.form['area2']
            ##
            lat1=""
            lon1=""
            lat2=""
            lon2=""
            for ds3 in df.values:
                if ds3[5]==district:
                    if ds3[2]==area:
                        lat1=ds3[8]
                        lon1=ds3[9]
                    if ds3[2]==area2:
                        lat2=ds3[8]
                        lon3=ds3[9]

                    '''lat11=lat1.split(".")
                    lat22=lat2.split(".")
                    lh1=int(lat11[1])

                    lk1=int(lat22[1])

                    #if lh1>lk1:'''
                        
            shutil.copy("static/dataset/mylat.html","templates/mydirection.html")
            aa1=area+", "+district
            aa2=area2+", "+district
            txt='<input type="hidden" id="t1" name="t1" value="'+aa1+'">'
            txt+='<input type="hidden" id="t2" name="t2" value="'+aa2+'">'
            ff=open("templates/mydirection.html","a")
            ff.write(txt)
            ff.close()

            ld=district+"|"+area+"|"+area2
            ff=open("static/location.txt","w")
            ff.write(ld)
            ff.close()
            
            print(area2)
            msg="ok"
            if area=="" or area2=="":
                s=1
            else:
                msg="yess"
                subprocess.call(["myfile2.bat"])
                

    return render_template('view_route.html',msg=msg,name=name,data=data,r_district=r_district,district=district,r_area=r_area,r_area2=r_area2,area=area,area2=area2,st=st)


@app.route('/get_lat', methods=['GET', 'POST'])
def get_lat():
    msg=""
    district=""
    r_area=[]
    r_area2=[]
    area=""
    area2=""
    data=[]
    
    st=""
    act=request.args.get("act")

    mycursor = mydb.cursor()

    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    dyt2=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    ff=open("static/location.txt","r")
    loc=ff.read()
    ff.close()
    ld=loc.split("|")
    district=ld[0]
    area=ld[1]
    area2=ld[2]

    #shutil.copy("static/dataset/mydata.html","templates/myroute1.html")
    aa1=area+", "+district
    aa2=area2+", "+district
    txt='<input type="hidden" id="t1" name="t1" value="'+aa1+'">'
    txt+='<input type="hidden" id="t2" name="t2" value="'+aa2+'">'
    

    c1=""
    c2=""
    c3=""
    c4=""
    c5=""
    c6=""
    txt2=""
    rrt=""
    crt=[]
    #if request.method=='POST':
    st="1"
    
    detail=request.form['detail']
    #print(detail)
    det=detail.split("\r\n")

    #print(det)

    
    print("lat")
    for dett in det:
        lc=dett.split(",")
        lat2=lc[0]
        lat22=lat2[0:6]

        mycursor.execute("SELECT * FROM ch_location where district=%s && status=1 && area=%s && dplace=%s",(district,area,area2))
        adat = mycursor.fetchall()
        


        
                        
        for ad in adat:
          
            '''lat1=str(ad[4])
            lat11=lat1[0:6]
                    
            if lat11==lat22:
                #print("##")
                #print(lat11)
                #print(ad[5])

                #print("**")
                #print(lat22)
                #print(lc[1])

                ln1=ad[5].split(".")
                ln2=ln1[1]
                ln3=ln2[0:3]
                ln4=int(ln3)

                ln41=ln4-30
                ln42=ln4+30

                ln22=lc[1].split(".")
                ln23=ln22[1]
                ln33=ln23[0:3]
                ln44=int(ln33)

                #print("=====")
                #print(ln41)
                #print(ln44)
                #print(ln42)
                #print("----")'''
                
            #if ln41<=ln44 and ln44<=ln42:
            rrt1=""
            if ad[2]=="Rape":
                c1+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "
                rrt+=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                rrt1=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                crt.append(rrt1)

            elif ad[2]=="Kidnapping and Abduction":
                c2+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "
                rrt+=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                rrt1=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                crt.append(rrt1)
                
            elif ad[2]=="Dowry Deaths":
                c3+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "
                rrt+=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                rrt1=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                crt.append(rrt1)

            elif ad[2]=="Assault on women with intent to outrage her modesty":
                c4+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "
                rrt+=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                rrt1=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                crt.append(rrt1)

            elif ad[2]=="Insult to modesty of Women":
                c5+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "
                rrt+=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                rrt1=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                crt.append(rrt1)

            elif ad[2]=="Cruelty by Husband or his Relatives":
                c6+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "
                rrt+=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                rrt1=ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+" - "+ad[2]+"|"
                crt.append(rrt1)

    crt1=unique(crt)
    crt2="".join(crt1)
    ff=open("static/details.txt","w")
    ff.write(crt2)
    ff.close()
    
    xc1="var locations = [ \n"
    xc1+="\n"+c1+"\n"
    xc1+="\n];\n"

    xc2="var locations2 = [ \n"
    xc2+="\n"+c2+"\n"
    xc2+="\n];\n"

    xc3="var locations3 = [ \n"
    xc3+="\n"+c3+"\n"
    xc3+="\n];\n"

    xc4="var locations4 = [ \n"
    xc4+="\n"+c4+"\n"
    xc4+="\n];\n"

    xc5="var locations5 = [ \n"
    xc5+="\n"+c5+"\n"
    xc5+="\n];\n"

    xc6="var locations6 = [ \n"
    xc6+="\n"+c6+"\n"
    xc6+="\n];\n"
                        
    '''txt2+='<input type="hidden" id="c1" name="c1" value="'+c1+'">'
    txt2+='<input type="hidden" id="c2" name="c2" value="'+c2+'">'
    txt2+='<input type="hidden" id="c3" name="c3" value="'+c3+'">'
    txt2+='<input type="hidden" id="c4" name="c4" value="'+c4+'">'
    txt2+='<input type="hidden" id="c5" name="c5" value="'+c5+'">'
    txt2+='<input type="hidden" id="c6" name="c6" value="'+c6+'">'
    '''

    ff=open("static/dataset/code3.txt","r")
    code1=ff.read()
    ff.close()

    ff=open("static/dataset/code4.txt","r")
    code2=ff.read()
    ff.close()

    xx=xc1+xc2+xc3+xc4+xc5+xc6

    tdata=code1+"\n"+xx+"\n"+code2

    
    ff=open("templates/myroute2.html","w")
    ff.write(tdata)
    ff.close()
    

    ff=open("templates/myroute2.html","a")
    ff.write(txt)
    ff.close()

    msg="yess"
    subprocess.call(["myfile.bat"])
                            

                        
                    

    return render_template('view_route.html',msg=msg,data=data,r_district=r_district,district=district,r_area=r_area,r_area2=r_area2,area=area,area2=area2,st=st)

@app.route('/details', methods=['GET', 'POST'])
def details():
    msg=""
    data=[]
    st=""
    ff=open("static/details.txt","r")
    dat=ff.read()
    ff.close()

    if dat=="":
        st="2"
    else:
        st="1"
        d1=dat.split("|")

        n=len(d1)-1
        i=0
        while i<n:
            data.append(d1[i])
            i+=1
        
            

    return render_template('details.html',msg=msg,st=st,data=data)

@app.route('/add_route', methods=['GET', 'POST'])
def add_route():
    msg=""
    uname=""
    district=""
    r_area=[]
    r_area2=[]
    area=""
    area2=""
    data=[]
    
    st=""
    act=request.args.get("act")
    #if 'username' in session:
    #    uname = session['username']
    #mycursor = mydb.cursor()
    #mycursor.execute("SELECT * FROM register where uname=%s",(uname,))
    #usr = mycursor.fetchone()
    #name=usr[1]

    mycursor = mydb.cursor()

    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    dyt2=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    r_district.sort()
    
    
    if request.method=='POST':
        st="1"
        
        district=request.form['district']
        if district=="":
            s=1
        else:
            for ds1 in df.values:
                if ds1[5]==district:
                    dyt.append(ds1[2])
                    dyt2.append(ds1[2])

            r_area=unique(dyt)
            r_area2=unique(dyt2)

            r_area.sort()
            r_area2.sort()

            area=request.form['area']
            area2=request.form['area2']
            shutil.copy("static/dataset/mylat2.html","templates/mydirection2.html")
            aa1=area+", "+district
            aa2=area2+", "+district
            txt='<input type="text" id="t1" name="t1" value="'+aa1+'">'
            txt+='<input type="text" id="t2" name="t2" value="'+aa2+'">'
            ff=open("templates/mydirection2.html","a")
            ff.write(txt)
            ff.close()

            ld=district+"|"+area+"|"+area2
            ff=open("static/location.txt","w")
            ff.write(ld)
            ff.close()
            
            print(area2)
            msg="ok"
            if area=="" or area2=="":
                s=1
            else:
                subprocess.call(["myfile3.bat"])

    return render_template('add_route.html',msg=msg,data=data,r_district=r_district,district=district,r_area=r_area,r_area2=r_area2,area=area,area2=area2,st=st)


@app.route('/get_lat2', methods=['GET', 'POST'])
def get_lat2():
    msg=""
    district=""
    r_area=[]
    r_area2=[]
    area=""
    area2=""
    data=[]
    
    st=""
    act=request.args.get("act")

    mycursor = mydb.cursor()

    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    dyt2=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    ff=open("static/location.txt","r")
    loc=ff.read()
    ff.close()
    ld=loc.split("|")
    district=ld[0]
    area=ld[1]
    area2=ld[2]

    #shutil.copy("static/dataset/mydata.html","templates/myroute1.html")
    aa1=area+", "+district
    aa2=area2+", "+district
    txt='<input type="text" id="t1" name="t1" value="'+aa1+'">'
    txt+='<input type="text" id="t2" name="t2" value="'+aa2+'">'
    

    c1=""
    c2=""
    c3=""
    c4=""
    c5=""
    c6=""
    txt2=""

       
    if request.method=='POST':
        st="1"
        
        detail=request.form['detail']

        ff=open("static/lat.txt","w")
        ff.write(detail)
        ff.close()
        return redirect(url_for('add_route1'))
        

    return render_template('get_lat2.html',msg=msg,data=data,r_district=r_district,district=district,r_area=r_area,r_area2=r_area2,area=area,area2=area2,st=st)


@app.route('/add_route1', methods=['GET', 'POST'])
def add_route1():
    msg=""
    district=""
    r_area=[]
    r_area2=[]
    area=""
    area2=""
    data=[]
    lat22=""
    lon22=""
    
    st=""
    act=request.args.get("act")

    mycursor = mydb.cursor()

    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    dyt2=[]
    cr=[]

    ##
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    y1=now.strftime("%Y")
    y11=int(y1)-1
    ydata=[]
    h=0
    while h<4:
        ydata.append(str(y11))
        y11-=1
        
        h+=1
    ##

        
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    ff=open("static/location.txt","r")
    loc=ff.read()
    ff.close()
    ld=loc.split("|")
    district=ld[0]
    area=ld[1]
    area2=ld[2]

    #shutil.copy("static/dataset/mydata.html","templates/myroute1.html")
    aa1=area+", "+district
    aa2=area2+", "+district
    txt='<input type="text" id="t1" name="t1" value="'+aa1+'">'
    txt+='<input type="text" id="t2" name="t2" value="'+aa2+'">'
    

    c1=""
    c2=""
    c3=""
    c4=""
    c5=""
    c6=""
    txt2=""

    ff=open("static/lat.txt","r")
    det1=ff.read()
    ff.close()

    #print(det1)
    
    det=det1.split("\n\n")
    tot=len(det)-1
    
    i=0
    j=2
    for dett in det:
        if i>1 and i<tot:
            #if i==j:
            #print(dett)
            dt=[]
            lc=dett.split(",")            
            
            la=lc[0].strip()
            lo=lc[1].strip()
            lat22=la
            lon22=lo
            if i==j:
                dt.append(la)
                dt.append(lo)
                data.append(dt)
                j+=10
        
        i+=1

    for ds3 in df.values:
        if ds3[5]==district:
            dyt.append(ds3[2])

    r_area=unique(dyt)
                    
    if request.method=='POST':
        st="1"
        area3=request.form['area']
        
        crime=request.form['crime']
        address=request.form['address']
        ch=request.form['ch']


        pincode=""
        for ds4 in df.values:
            if ds4[5]==district and ds4[2]==area:
                pincode=ds4[1]

        
        mycursor.execute("SELECT max(id)+1 FROM ch_location")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        loo=ch.split(",")
        lat=loo[0].strip()
        lon=loo[1].strip()

        rn=randint(1,4)
        rn1=rn-1
        year=ydata[rn1]
        
        sql = "INSERT INTO ch_location(id,district,crime,area,lat,lon,address,pincode,year,status,dplace) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)"
        val = (maxid,district,crime,area3,lat,lon,address,pincode,year,'1',area2)
        mycursor.execute(sql, val)
        mydb.commit()

        msg="ok"


    if act=="yes":
        #ff=open("templates/myroute1.html","a")
        #ff.write(txt)
        #ff.close()
        #subprocess.call(["myfile3.bat"])
       

        mycursor.execute("SELECT * FROM ch_location where district=%s",(district,))
        adat = mycursor.fetchall()
                        
        for ad in adat:
          
            lat1=str(ad[4])
            lat11=lat1[0:6]
                    
            if lat11==lat22:
                #print("##")
                #print(lat11)
                #print(ad[5])

                #print("**")
                #print(lat22)
                #print(lc[1])

                ln1=ad[5].split(".")
                ln2=ln1[1]
                ln3=ln2[0:3]
                ln4=int(ln3)

                ln41=ln4-30
                ln42=ln4+30

                ln22=lc[1].split(".")
                ln23=ln22[1]
                ln33=ln23[0:3]
                ln44=int(ln33)

                #print("=====")
                #print(ln41)
                #print(ln44)
                #print(ln42)
                #print("----")
                
                if ln41<=ln44 and ln44<=ln42:
                
                    if ad[2]=="Rape":
                        c1+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "

                    elif ad[2]=="Kidnapping and Abduction":
                        c2+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "
                    elif ad[2]=="Dowry Deaths":
                        c3+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "

                    elif ad[2]=="Assault on women with intent to outrage her modesty":
                        c4+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "

                    elif ad[2]=="Insult to modesty of Women":
                        c5+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "

                    elif ad[2]=="Cruelty by Husband or his Relatives":
                        c6+="['"+ad[6]+" "+ad[3]+", "+ad[1]+", "+ad[7]+"<br> ("+ad[2]+")', "+ad[4]+", "+ad[5]+", 4], "

        xc1="var locations = [ \n"
        xc1+="\n"+c1+"\n"
        xc1+="\n];\n"

        xc2="var locations2 = [ \n"
        xc2+="\n"+c2+"\n"
        xc2+="\n];\n"

        xc3="var locations3 = [ \n"
        xc3+="\n"+c3+"\n"
        xc3+="\n];\n"

        xc4="var locations4 = [ \n"
        xc4+="\n"+c4+"\n"
        xc4+="\n];\n"

        xc5="var locations5 = [ \n"
        xc5+="\n"+c5+"\n"
        xc5+="\n];\n"

        xc6="var locations6 = [ \n"
        xc6+="\n"+c6+"\n"
        xc6+="\n];\n"
                            
        '''txt2+='<input type="hidden" id="c1" name="c1" value="'+c1+'">'
        txt2+='<input type="hidden" id="c2" name="c2" value="'+c2+'">'
        txt2+='<input type="hidden" id="c3" name="c3" value="'+c3+'">'
        txt2+='<input type="hidden" id="c4" name="c4" value="'+c4+'">'
        txt2+='<input type="hidden" id="c5" name="c5" value="'+c5+'">'
        txt2+='<input type="hidden" id="c6" name="c6" value="'+c6+'">'
        '''

        ff=open("static/dataset/code1.txt","r")
        code1=ff.read()
        ff.close()

        ff=open("static/dataset/code2.txt","r")
        code2=ff.read()
        ff.close()

        xx=xc1+xc2+xc3+xc4+xc5+xc6

        tdata=code1+"\n"+xx+"\n"+code2

        
        ff=open("templates/myroute1.html","w")
        ff.write(tdata)
        ff.close()

        ff=open("templates/myroute1.html","a")
        ff.write(txt)
        ff.close()
        subprocess.call(["myfile2.bat"])
                            

                        
                    

    return render_template('add_route1.html',msg=msg,act=act,data=data,r_district=r_district,district=district,r_area=r_area,r_area2=r_area2,area=area,area2=area2,st=st)


@app.route('/map3', methods=['GET', 'POST'])
def map3():
    msg=""
    data=[]

    latt=""
    lonn=""
    ff=open("static/lat.txt","r")
    det1=ff.read()
    ff.close()

    #print(det1)
    
    det=det1.split("\n\n")
    tot=len(det)-1
    
    i=0
    j=2
    for dett in det:
        if i>1 and i<tot:

            
            #if i==j:
            #print(dett)
            dt=[]
            lc=dett.split(",")            
            
            la=lc[0].strip()
            lo=lc[1].strip()
            lat22=la
            lon22=lo

            latt=la
            lonn=lo
            
            
            if i==j:
                dt.append(la)
                dt.append(lo)
                data.append(dt)
                j+=10
        
        i+=1

    return render_template('map3.html',msg=msg,data=data,latt=latt,lonn=lonn)
    

@app.route('/map_wayroute2', methods=['GET', 'POST'])
def map_wayroute2():
    msg=""
    msg=""
    uname=""
    district=""
    r_area=[]
    r_area2=[]
    area=""
    area2=""
    data=[]
    
    st=""
    act=request.args.get("act")
    #if 'username' in session:
    #    uname = session['username']
    #mycursor = mydb.cursor()
    #mycursor.execute("SELECT * FROM register where uname=%s",(uname,))
    #usr = mycursor.fetchone()
    #name=usr[1]

    mycursor = mydb.cursor()

    df=pd.read_csv('static/dataset/crime_postal.csv')
    df.head()

    dst=[]
    dyt=[]
    dyt2=[]
    cr=[]
    for ds in df.values:
        dst.append(ds[5])
        
    r_district=unique(dst)
    
    
    '''if request.method=='POST':
        st="1"
        
        district=request.form['district']
        if district=="":
            s=1
        else:
            for ds1 in df.values:
                if ds1[5]==district:
                    dyt.append(ds1[2])
                    dyt2.append(ds1[2])

            r_area=unique(dyt)
            r_area2=unique(dyt2)

            area=request.form['area']
            area2=request.form['area2']

            print(area2)'''
            
    return render_template('map_wayroute2.html',msg=msg,data=data,r_district=r_district,district=district,r_area=r_area,r_area2=r_area2,area=area,area2=area2,st=st)

@app.route('/location', methods=['GET', 'POST'])
def location():
    msg=""

   
        
    return render_template('location.html',msg=msg)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg=""

    df=pd.read_csv('static/dataset/crimes.csv')
    df.head()
        
    return render_template('admin.html',msg=msg)

@app.route('/process1', methods=['GET', 'POST'])
def process1():
    msg=""
    data=[]
    df=pd.read_csv('static/dataset/crimes.csv')
    dat=df.head(200)

    for ss in dat.values:
        data.append(ss)
    
    return render_template('process1.html',data=data)

@app.route('/process2', methods=['GET', 'POST'])
def process2():
    msg=""
    mem=0
    cnt=0
    cols=0
    filename = 'static/dataset/crimes.csv'
    data1 = pd.read_csv(filename, header=0)
    data2 = list(data1.values.flatten())
    cname=[]
    data=[]
    dtype=[]
    dtt=[]
    nv=[]
    i=0
    
    sd=len(data1)
    rows=len(data1.values)
    
    #print(data1.columns)
    col=data1.columns
    #print(data1[0])
    for ss in data1.values:
        cnt=len(ss)
        

    i=0
    while i<cnt:
        j=0
        x=0
        for rr in data1.values:
            dt=type(rr[i])
            if rr[i]!="":
                x+=1
            
            j+=1
        dtt.append(dt)
        nv.append(str(x))
        
        i+=1

    arr1=np.array(col)
    arr2=np.array(nv)
    data3=np.vstack((arr1, arr2))


    arr3=np.array(data3)
    arr4=np.array(dtt)
    
    data=np.vstack((arr3, arr4))
   
    print(data)
    cols=cnt
    mem=float(rows)*0.75

    return render_template('process2.html',data=data, msg=msg, rows=rows, cols=cols, dtype=dtype, mem=mem)


@app.route('/process3', methods=['GET', 'POST'])
def process3():
    df=pd.read_csv('static/dataset/crimes.csv')
    df.head()
    df.drop('Unnamed: 0',axis=1,inplace=True)
    df['STATE/UT'].unique()
    df.loc[df['STATE/UT'] == 'A&N Islands', 'STATE/UT'] = 'A & N ISLANDS'
    df.loc[df['STATE/UT'] == 'D&N Haveli', 'STATE/UT'] = 'D & N HAVELI'
    df.loc[df['STATE/UT'] == 'Delhi UT', 'STATE/UT'] = 'DELHI'

    #converting all the state names to capitals
    df['STATE/UT'] = pd.Series(str.upper(i) for i in df['STATE/UT'])
    df['DISTRICT'] = pd.Series(str.upper(i) for i in df['DISTRICT'])
    #stroring the sum of all crimes comitted within a state statewise
    state_all_crimes = df.groupby('STATE/UT').sum()

    #droping the sum of year column
    state_all_crimes.drop('Year',axis=1,inplace=True)

    #adding a column containig the total crime against women in that state
    col_list= list(state_all_crimes)
    state_all_crimes['Total']=state_all_crimes[col_list].sum(axis=1)
    all_crimes = state_all_crimes

    #sorting the statewise crime from highest to lowest
    state_all_crimes.sort_values('Total',ascending=False)

    state_all_crimes=state_all_crimes.reset_index()
    total_df=state_all_crimes.sum(axis=0).reset_index()
    tf=pd.DataFrame(total_df)

    tf=tf.drop([0])
    tf=tf.drop([8])

    sorted_df = state_all_crimes.sort_values('Total',ascending=False)
    '''fig = px.bar( x=tf["index"],y=tf[0], color=tf[0], 
                 labels={'x': "Crimes", 'y': "Count"}, title="Total Cases", 
                 color_continuous_scale='burg')
    fig.show()'''

    #sates v/s total crimes
    '''sorted_df = state_all_crimes.sort_values('Total',ascending=False)
    fig = px.bar( x=sorted_df['STATE/UT'],y=sorted_df["Total"], color=sorted_df["Total"], 
                 labels={'x': "States", 'y': "Count"}, title="Total Cases", 
                 color_continuous_scale='burg')
    fig.show()'''

    '''fig = px.bar( x=state_all_crimes['STATE/UT'],y=state_all_crimes["Rape"], color=state_all_crimes["Rape"], 
             labels={'x': "States", 'y': "Count"}, title="Rape Cases", 
             color_continuous_scale='burg')
    fig.show()'''

    #states v/s  kidnapping and abduction

    '''fig = px.bar( x=state_all_crimes['STATE/UT'],y=state_all_crimes["Kidnapping and Abduction"], color=state_all_crimes["Kidnapping and Abduction"], 
                 labels={'x': "States", 'y': "Count"}, title="Kidnapping and Abduction Cases", 
                 color_continuous_scale='burg')
    fig.show()'''

    #states v/s Importation of Girls

    '''importation_df = state_all_crimes.copy()
    importation_df.loc[importation_df['Importation of Girls'] <= 50, 'STATE/UT'] = 'Others' # Represent only large countries
    fig = px.pie(importation_df, values='Importation of Girls', names='STATE/UT', title="Importation of Girls", 
                color_discrete_sequence=px.colors.sequential.Teal_r)
    fig.update_traces(textposition='inside', textinfo='label+value',
                    marker=dict(line=dict(color='#000000', width=2)))
    #fig.update_layout(annotations=[dict(text='count', x=0.5, y=0.5, font_size=20, showarrow=False)])
    fig.show()'''

    return render_template('process3.html')

@app.route('/process4', methods=['GET', 'POST'])
def process4():
    data=[]
    data2=[]
    df=pd.read_csv('static/dataset/crimes.csv')
    df.head()
    df.drop('Unnamed: 0',axis=1,inplace=True)
    df['STATE/UT'].unique()
    df.loc[df['STATE/UT'] == 'A&N Islands', 'STATE/UT'] = 'A & N ISLANDS'
    df.loc[df['STATE/UT'] == 'D&N Haveli', 'STATE/UT'] = 'D & N HAVELI'
    df.loc[df['STATE/UT'] == 'Delhi UT', 'STATE/UT'] = 'DELHI'

    #converting all the state names to capitals
    df['STATE/UT'] = pd.Series(str.upper(i) for i in df['STATE/UT'])
    df['DISTRICT'] = pd.Series(str.upper(i) for i in df['DISTRICT'])
    #stroring the sum of all crimes comitted within a state statewise
    state_all_crimes = df.groupby('STATE/UT').sum()

    #droping the sum of year column
    state_all_crimes.drop('Year',axis=1,inplace=True)

    #adding a column containig the total crime against women in that state
    col_list= list(state_all_crimes)
    state_all_crimes['Total']=state_all_crimes[col_list].sum(axis=1)
    all_crimes = state_all_crimes

    #sorting the statewise crime from highest to lowest
    state_all_crimes.sort_values('Total',ascending=False)

    state_all_crimes=state_all_crimes.reset_index()
    total_df=state_all_crimes.sum(axis=0).reset_index()
    tf=pd.DataFrame(total_df)

    tf=tf.drop([0])
    tf=tf.drop([8])

    sorted_df = state_all_crimes.sort_values('Total',ascending=False)
    ##
    dat=all_crimes = all_crimes.reset_index()
    for ss in dat.values:
        data.append(ss)

    all_crimes.shape
    #finding the mean number of crimes
    m=all_crimes['Total'].mean()
    print('mean=',m)

    #finding the quantiles 
    q = np.quantile(all_crimes['Total'],[0.25,0.75])
    print(q)
    l=q[0]
    u=q[1]

    #copying the state_all_crimes to a new dataframe to normalise values and predict
    df_kmeans = all_crimes.loc[:,all_crimes.columns!="STATE/UT"]

    #adding an additional column called output
    output=[]
    for i in df_kmeans['Total']:
        if i >= m:
            output.append(1)#redzone
        elif m > i:
            output.append(0)#safe

    all_crimes['output']=output
    df_kmeans_y=all_crimes['output']

    #feature scaling
    from sklearn.preprocessing import MinMaxScaler
    cols = df_kmeans.columns

    ms=MinMaxScaler()

    df_kmeans = ms.fit_transform(df_kmeans)
    df_kmeans = pd.DataFrame(df_kmeans,columns=[cols])
    df_kmeans.head()
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2, random_state=0) 
    kmeans.fit(df_kmeans)
    kmeans.inertia_
    #checking the accuracy

    labels = kmeans.labels_

    # check how many of the samples were correctly labeled
    correct_labels = sum(df_kmeans_y == labels)

    print('labels:',labels)
    print('df_kmeans output:',df_kmeans_y)
    print("Result: %d out of %d samples were correctly labeled." % (correct_labels, df_kmeans_y.size))

    #based on the prediction of the k means algorithm classifying the states 
    #as safe or unsafe for women
    final=[]
    for i in range(len(labels)):
        state=all_crimes['STATE/UT'][i]
        label = labels[i]
        if label == 1:
            final.append([state,'unsafe'])
            
        else:
            final.append([state,'safe'])
            

    dat2=final_df = pd.DataFrame(final, columns=['STATES/UT', 'SAFE/UNSAFE'])
    
    #final_df
    ##
    for ss2 in dat2.values:
        data2.append(ss2)

    return render_template('process4.html',data=data,data2=data2)

#XDT - Explainable Decision Tree
def DecisionTree():
    counts = {} 
    for row in rows:
        label = row[-1]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts

def max_label(dict):
    max_count = 0
    label = ""

    for key, value in dict.items():
        if dict[key] > max_count:
            max_count = dict[key]
            label = key

    return label

def is_numeric(value):
    """Test if a value is numeric."""
    return isinstance(value, int) or isinstance(value, float)


class Question:
    

    def __init__(self, column, value, header):
        self.column = column
        self.value = value
        self.header = header

    def match(self, example):
        # Compare the feature value in an example to the
        # feature value in this question.
        val = example[self.column]
        if is_numeric(val):
            return val >= self.value
        else:
            return val == self.value

    def __repr__(self):
        # This is just a helper method to print
        # the question in a readable format.
        condition = "=="
        if is_numeric(self.value):
            condition = ">="
        return "Is %s %s %s?" % (
            self.header[self.column], condition, str(self.value))


def partition(rows, question):
   
    true_rows, false_rows = [], []
    for row in rows:
        if question.match(row):
            true_rows.append(row)
        else:
            false_rows.append(row)
    return true_rows, false_rows


def gini(rows):
    counts = class_counts(rows)
    impurity = 1
    for lbl in counts:
        prob_of_lbl = counts[lbl] / float(len(rows))
        impurity -= prob_of_lbl**2
    return impurity


def entropy(rows):

    # compute the entropy.
    entries = class_counts(rows)
    avg_entropy = 0
    size = float(len(rows))
    for label in entries:
        prob = entries[label] / size
        avg_entropy = avg_entropy + (prob * math.log(prob, 2))
    return -1*avg_entropy


def info_gain(left, right, current_uncertainty):
    """Information Gain.

    The uncertainty of the starting node, minus the weighted impurity of
    two child nodes.
    """
    p = float(len(left)) / (len(left) + len(right))

    ## TODO: Step 3, Use Entropy in place of Gini
    return current_uncertainty - p * entropy(left) - (1 - p) * entropy(right)

def find_best_split(rows, header):
    """Find the best question to ask by iterating over every feature / value
    and calculating the information gain."""
    best_gain = 0  # keep track of the best information gain
    best_question = None  # keep train of the feature / value that produced it
    current_uncertainty = entropy(rows)
    n_features = len(rows[0]) - 1  # number of columns

    for col in range(n_features):  # for each feature

        values = set([row[col] for row in rows])  # unique values in the column

        for val in values:  # for each value

            question = Question(col, val, header)

            # try splitting the dataset
            true_rows, false_rows = partition(rows, question)

            # Skip this split if it doesn't divide the
            # dataset.
            if len(true_rows) == 0 or len(false_rows) == 0:
                continue

            # Calculate the information gain from this split
            gain = info_gain(true_rows, false_rows, current_uncertainty)
            if gain >= best_gain:
                best_gain, best_question = gain, question

    return best_gain, best_question

class Leaf:
    def __init__(self, rows, id, depth):
        self.predictions = class_counts(rows)
        self.predicted_label = max_label(self.predictions)
        self.id = id
        self.depth = depth

class Decision_Node:
    """A Decision Node asks a question.

    This holds a reference to the question, and to the two child nodes.
    """

    def __init__(self,
                 question,
                 true_branch,
                 false_branch,
                 depth,
                 id,
                 rows):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.depth = depth
        self.id = id
        self.rows = rows

def build_tree(rows, header, depth=0, id=0):
    
    gain, question = find_best_split(rows, header)
    if gain == 0:
        return Leaf(rows, id, depth)

    # If we reach here, we have found a useful feature / value
    # to partition on.
    # nodeLst.append(id)
    true_rows, false_rows = partition(rows, question)

    # Recursively build the true branch.
    true_branch = build_tree(true_rows, header, depth + 1, 2 * id + 2)

    # Recursively build the false branch.
    false_branch = build_tree(false_rows, header, depth + 1, 2 * id + 1)
    return Decision_Node(question, true_branch, false_branch, depth, id, rows)

def prune_tree(node, prunedList):
    if int(node.id) in prunedList:
        return Leaf(node.rows, node.id, node.depth)

    # Call this function recursively on the true branch
    node.true_branch = prune_tree(node.true_branch, prunedList)

    # Call this function recursively on the false branch
    node.false_branch = prune_tree(node.false_branch, prunedList)

    return node

def classify(row, node):
    """See the 'rules of recursion' above."""

    # Base case: we've reached a leaf
    if isinstance(node, Leaf):
        return node.predicted_label

    # Decide whether to follow the true-branch or the false-branch.
    # Compare the feature / value stored in the node,
    # to the example we're considering.
    if node.question.match(row):
        return classify(row, node.true_branch)
    else:
        return classify(row, node.false_branch)

def print_tree(node, spacing=""):
    """World's most elegant tree printing function."""

    # Base case: we've reached a leaf
    if isinstance(node, Leaf):
        print(spacing + "Leaf id: " + str(node.id) + " Predictions: " + str(node.predictions) + " Label Class: " + str(node.predicted_label))
        return

    # Print the question at this node
    print(spacing + str(node.question) + " id: " + str(node.id) + " depth: " + str(node.depth))

    # Call this function recursively on the true branch
    print(spacing + '--> True:')
    print_tree(node.true_branch, spacing + "  ")

    # Call this function recursively on the false branch
    print(spacing + '--> False:')
    print_tree(node.false_branch, spacing + "  ")


def print_leaf(counts):
    """A nicer way to print the predictions at a leaf."""
    total = sum(counts.values()) * 1.0
    probs = {}
    for lbl in counts.keys():
        probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
    return probs
def getLeafNodes(node, leafNodes =[]):

    # Base case
    if isinstance(node, Leaf):
        leafNodes.append(node)
        return

    # Recursive right call for true values
    getLeafNodes(node.true_branch, leafNodes)

    # Recursive left call for false values
    getLeafNodes(node.false_branch, leafNodes)

    return leafNodes

def getInnerNodes(node, innerNodes =[]):

    # Base case
    if isinstance(node, Leaf):
        return
    innerNodes.append(node)
    getInnerNodes(node.true_branch, innerNodes)
    getInnerNodes(node.false_branch, innerNodes)

    return innerNodes

def computeAccuracy(rows, node):

    count = len(rows)
    if count == 0:
        return 0

    accuracy = 0
    for row in rows:
        # last entry of the column is the actual label
        if row[-1] == classify(row, node):
            accuracy += 1
    return round(accuracy/count, 2)

from sklearn.tree import DecisionTreeClassifier


def model():

    crime = load_crime()
    X = crime.data
    y = crime.target

    # Train a decision tree classifier
    clf = DecisionTreeClassifier()
    clf.fit(X, y)

    dot_data = tree.export_graphviz(clf, out_file=None, 
                             feature_names=crime.feature_names,  
                             class_names=crime.target_names,  
                             filled=True, rounded=True,  
                             special_characters=True)  
    graph = graphviz.Source(dot_data)  
    graph.render("crime_decision_tree")
    perm = PermutationImportance(clf, random_state=1).fit(X, y)
    eli5.show_weights(perm, feature_names = crime.feature_names)
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X)
    shap.summary_plot(shap_values, X, feature_names=crime.feature_names)

##################
    
@app.route('/process5', methods=['GET', 'POST'])
def process5():
    data=[]
    data2=[]
    df=pd.read_csv('static/dataset/crimes.csv')
    df.head()
    df.drop('Unnamed: 0',axis=1,inplace=True)
    df['STATE/UT'].unique()
    df.loc[df['STATE/UT'] == 'A&N Islands', 'STATE/UT'] = 'A & N ISLANDS'
    df.loc[df['STATE/UT'] == 'D&N Haveli', 'STATE/UT'] = 'D & N HAVELI'
    df.loc[df['STATE/UT'] == 'Delhi UT', 'STATE/UT'] = 'DELHI'

    #converting all the state names to capitals
    df['STATE/UT'] = pd.Series(str.upper(i) for i in df['STATE/UT'])
    df['DISTRICT'] = pd.Series(str.upper(i) for i in df['DISTRICT'])
    #stroring the sum of all crimes comitted within a state statewise
    state_all_crimes = df.groupby('STATE/UT').sum()

    #droping the sum of year column
    state_all_crimes.drop('Year',axis=1,inplace=True)

    #adding a column containig the total crime against women in that state
    col_list= list(state_all_crimes)
    state_all_crimes['Total']=state_all_crimes[col_list].sum(axis=1)
    all_crimes = state_all_crimes

    #sorting the statewise crime from highest to lowest
    state_all_crimes.sort_values('Total',ascending=False)

    state_all_crimes=state_all_crimes.reset_index()
    total_df=state_all_crimes.sum(axis=0).reset_index()
    tf=pd.DataFrame(total_df)

    tf=tf.drop([0])
    tf=tf.drop([8])

    sorted_df = state_all_crimes.sort_values('Total',ascending=False)
    ##
    dat=all_crimes = all_crimes.reset_index()
    for ss in dat.values:
        dt=[]
        dt.append(ss[0])
      
        f1=float(ss[8])
        if f1>200000:
            dt.append("Not Safety")
        elif f1>100000:
            dt.append("Medium Safety")

        elif f1>50000:
            dt.append("Low Safety")
        else:
            dt.append("Safety")        

        dt.append(f1)
        data.append(dt)

    all_crimes.shape
    #finding the mean number of crimes
    m=all_crimes['Total'].mean()
    print('mean=',m)

    #finding the quantiles 
    q = np.quantile(all_crimes['Total'],[0.25,0.75])
    print(q)
    l=q[0]
    u=q[1]

    #copying the state_all_crimes to a new dataframe to normalise values and predict
    df_kmeans = all_crimes.loc[:,all_crimes.columns!="STATE/UT"]

    #adding an additional column called output
    output=[]
    for i in df_kmeans['Total']:
        if i >= m:
            output.append(1)#redzone
        elif m > i:
            output.append(0)#safe

    all_crimes['output']=output
    df_kmeans_y=all_crimes['output']

    #feature scaling
    from sklearn.preprocessing import MinMaxScaler
    cols = df_kmeans.columns

    ms=MinMaxScaler()

    df_kmeans = ms.fit_transform(df_kmeans)
    df_kmeans = pd.DataFrame(df_kmeans,columns=[cols])
    df_kmeans.head()
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2, random_state=0) 
    kmeans.fit(df_kmeans)
    kmeans.inertia_
    #checking the accuracy

    labels = kmeans.labels_

    # check how many of the samples were correctly labeled
    correct_labels = sum(df_kmeans_y == labels)

    print('labels:',labels)
    print('df_kmeans output:',df_kmeans_y)
    print("Result: %d out of %d samples were correctly labeled." % (correct_labels, df_kmeans_y.size))

    #based on the prediction of the k means algorithm classifying the states 
    #as safe or unsafe for women
    final=[]
    for i in range(len(labels)):
        state=all_crimes['STATE/UT'][i]
        label = labels[i]
        if label == 1:
            final.append([state,'unsafe'])
            
        else:
            final.append([state,'safe'])
            

    dat2=final_df = pd.DataFrame(final, columns=['STATES/UT', 'SAFE/UNSAFE'])
    
    #final_df
    ##
    for ss2 in dat2.values:
        data2.append(ss2)

    return render_template('process5.html',data=data,data2=data2)
  



##########################
@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


