import locale
import os
import tabula
import json
import codecs
import pyodbc
import pandas as pd
import requests
from bs4 import BeautifulSoup
locale.setlocale(locale.LC_ALL, 'tr_TR')
#Defined scrapping url
url= "https://www.bp.com/tr_tr/turkey/home/urun-ve-hizmetler/akaryakit/bp-akaryakitlari/bp-otogaz.html"
#Fetch url with get request
req=requests.get(url)
#Starting scrapping session
soup =BeautifulSoup(req.text,"html.parser")
pdf_path=soup.find("a",{"class":"nr-linkcta__link-list-anchor"})
#Test fetch true link
print(pdf_path['href'])
#Url creating with string builder
file_path="https://www.bp.com"+pdf_path['href']
#Fetch and convert pdf to Json file format
tabula.convert_into(file_path,"read.json",pages="all",output_format="json")
#Read json file for getting true form
with codecs.open("read.json","r","iso8859-9") as json_file:
    data=json.load(json_file)
#Define temporary json file with true form
with codecs.open("output.json","w","iso8859-9")as output:
    output.write('[')
    i=0
    #Create usable form of json file
    for item in data[0]["data"]:
        elem=item[0]["text"].split()

        if (len(elem) == 2):
            dictinary={
                 "il":str(elem[0]),
                 "otogaz":str(elem[1])
            }
            json_object= json.dumps(dictinary,indent=2,ensure_ascii=False)
            output.write(json_object)
            if i < (len(data[0]["data"])-1):
                output.write(',')
            else:
                output.write(']')
        i+=1
output.close()
#Connedt sql server to push json file elements
conn = pyodbc.connect(r'Driver=SQL Server;Server=DSK6;Database=GasStation;Trusted_Connection=yes;')
cursor=conn.cursor()
j=open("output.json","r")
json_data=json.load(j)
df=pd.read_json(json.dumps(json_data))
for item in df.index:
    print (str(df['il'][item])+" "+str(df['otogaz'][item]))
    cursor.execute("exec AddtoBPLpg @il='"+str(df['il'][item])+"', @otogaz='"+str(df['otogaz'][item])+"'").commit()
j.close()
#Remove temp files
os.remove('read.json')
os.remove("output.json")
conn.close()