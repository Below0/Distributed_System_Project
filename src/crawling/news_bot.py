#!/usr/bin/env python
# coding: utf-8

# In[48]:


import os
import sys
import urllib.request
from urllib.parse import *
import requests
from bs4 import BeautifulSoup
import json
import re

# 오픈 API 아이디, 비번
client_id = "qm7U_KZ7JM07gFwBDy9i"
client_secret = "I5N09EqxQq"

keywords = ['현대자동차']

display = str(100) # 각 키워드 당 검색해서 저장할 기사 수

def remove_tag(content):
    cleanr =re.compile('<.*?>')
    result = re.sub(cleanr, '', content)
    return result

def get_bs_obj(url):
    result = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    bs_obj = BeautifulSoup(result.content, "html.parser")
    return bs_obj
    

# Input(str) : 뉴스에 검색할 단어 넣기
def news_search(min_name):
    encText = urllib.parse.quote(min_name)
    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText +         "&display=" + display + "&sort=sim"
         # json 결과
    # url = "https://openapi.naver.com/v1/search/news.xml?query=" + encText # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)


    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        #response_body_str = response.read().decode('utf-8')
        response_body_str = response.read().decode('utf-8')
        json_acceptable_string = response_body_str.replace("'", "\"")
        response_body = json.loads(response_body_str)
        news_list = []
        for i in range(0, len(response_body['items'])):
            if response_body['items'][i]['link'][13:18] != 'naver':
                continue
            
            article_bs = get_bs_obj(response_body['items'][i]['link'])
            article_text = article_bs.find('div', id = 'articleBodyContents').text
            
            
            contents_list = article_text.split('\n')

            for j in range(8,len(contents_list)):
                if len(contents_list[j]) > 10:
                    contents_body = contents_list[j].strip()
                    break
            
            endpoint = contents_body.find('▶')
            if endpoint > -1:
                contents_body = contents_body[:endpoint]
            
            news_list.append({
                'title':remove_tag(response_body['items'][i]['title']),
                'link': response_body['items'][i]['link'],
                'body': contents_body
            })
            
        return news_list

    else:
        print("Error Code:" + rescode)

if __name__ == '__main__':
    for keyword in keywords:
        result = news_search(keyword)
        print(result)


# In[ ]:





# In[ ]:




