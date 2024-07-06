# main.py
import os
import base64
import io
import math
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
import mysql.connector
import hashlib
import datetime
import calendar
import random
from random import randint
from urllib.request import urlopen
import webbrowser
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np



df=pd.read_csv('crime_data.csv')
df.head()

data3=[]
i=0
for d1 in df.values:
    #if d1[3]==2022:
    #    print(d1[3])
    #    print(d1[1])
    if d1[1]=="TAMIL NADU" or d1[1]=="Tamil Nadu":
        dt=[]
        #print(d1[3])  
        #print(d1[5])
        rn1=0
        rn2=0
        rn3=0
        rn4=0
        rn5=0
        rn6=0
        if int(d1[4])==0:
            rn1=randint(0,2)
        else:
            rn1=randint(2,4)

        if int(d1[5])==0:
            rn2=randint(0,2)
        else:
            rn2=randint(2,4)

        if int(d1[6])==0:
            rn3=randint(0,2)
        else:
            rn3=randint(2,4)

        if int(d1[7])==0:
            rn4=randint(0,2)
        else:
            rn4=randint(2,4)

        if int(d1[8])==0:
            rn5=randint(0,2)
        else:
            rn5=randint(2,4)

        if int(d1[9])==0:
            rn6=randint(0,2)
        else:
            rn6=randint(2,4)

        a1=int(d1[4])+rn1
        a2=int(d1[5])+rn2
        a3=int(d1[6])+rn3
        a4=int(d1[7])+rn4
        a5=int(d1[8])+rn5
        a6=int(d1[9])+rn6
            
        dt.append(d1[0])
        dt.append(d1[1])
        dt.append(d1[2])
        dt.append(d1[3])
        dt.append(a1)
        dt.append(a2)
        dt.append(a3)
        dt.append(a4)
        dt.append(a5)
        dt.append(a6)
        dt.append(d1[10])
        data3.append(dt)
       
        i+=1
##
    
for ds in data3:
    #print(ds[3])
    with open('crime2.csv','a',newline='') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(ds)

