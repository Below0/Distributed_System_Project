#!/usr/bin/env python
# coding: utf-8

# In[95]:


import os
import sys
import urllib.request
from urllib.parse import *
import requests
from bs4 import BeautifulSoup
import json
import re
import json
import pymysql

# with statement

def connect_db():
    with open('./config/db.json') as json_file:
        config_data = json.load(json_file)

    db = pymysql.connect(
        user=config_data['id'],
        port=3306,
        passwd=config_data['pw'], 
        host=config_data['addr'], 
        db='ssu', 
        charset='utf8'
    )
    
    return db


def remove_tag(content):
    cleanr =re.compile('<.*?>')
    result = re.sub(cleanr, '', content)
    return result

def get_bs_obj(url):
    result = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    bs_obj = BeautifulSoup(result.content, "html.parser")
    return bs_obj

def crawl_kospi(size):
    n = int(size / 10)
    url = 'https://finance.naver.com/sise/entryJongmok.nhn?&page='
    kospi = []
    
    for i in range(0,n):
        bs = get_bs_obj(url+str(i+1))
        lst = bs.find_all("td", class_="ctg")
        for item in lst:
            a = item.find('a')
            link = a.get('href')
            code = link[-6:]
            name = item.text
            kospi.append([name,code])
    
    return kospi


if __name__ == "__main__":
    kospi100 = crawl_kospi(100)
    db = connect_db()
    db_cursor = db.cursor()
    sql = '''INSERT INTO `kospi` (name, code) 
        VALUES (%s,%s);'''
    db_cursor.executemany(sql,kospi100)
    db.commit()


# In[70]:





# In[ ]:




