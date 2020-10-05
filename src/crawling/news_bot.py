import os
import sys
import urllib.request
from urllib.parse import *
import requests
from bs4 import BeautifulSoup
import json
import re
import pymysql

# 오픈 API 아이디, 비번
with open('./config/api.json') as json_file:
    config_data = json.load(json_file)

client_id = config_data['id']
client_secret = config_data['pw']

display = str(100)  # 각 키워드 당 검색해서 저장할 기사 수


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
    cleanr = re.compile('<.*?>')
    result = re.sub(cleanr, '', content)
    return result


def get_bs_obj(url):
    result = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    bs_obj = BeautifulSoup(result.content, "html.parser")
    return bs_obj


# Input(str) : 뉴스에 검색할 단어 넣기
def news_search(min_name):
    encText = urllib.parse.quote(min_name)
    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + \
          "&display=" + display + "&sort=sim"
    # json 결과
    # url = "https://openapi.naver.com/v1/search/news.xml?query=" + encText # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if (rescode == 200):
        # response_body_str = response.read().decode('utf-8')
        response_body_str = response.read().decode('utf-8')
        json_acceptable_string = response_body_str.replace("'", "\"")
        response_body = json.loads(response_body_str)
        news_list = []
        for i in range(0, len(response_body['items'])):
            if response_body['items'][i]['link'][13:18] != 'naver':
                continue

            article_bs = get_bs_obj(response_body['items'][i]['link'])
            article_text = article_bs.find('div', id='articleBodyContents').text

            contents_list = article_text.split('\n')

            for j in range(8, len(contents_list)):
                if len(contents_list[j]) > 10:
                    contents_body = contents_list[j].strip()
                    break

            endpoint = contents_body.find('▶')
            if endpoint > -1:
                contents_body = contents_body[:endpoint]

            news_list.append({
                'title': remove_tag(response_body['items'][i]['title']),
                'link': response_body['items'][i]['link'],
                'body': contents_body
            })

        return news_list

    else:
        print("Error Code:" + rescode)


if __name__ == '__main__':
    db = connect_db()
    db_cursor = db.cursor()
    sql = "SELECT `name` FROM `kospi`;"
    db_cursor.execute(sql)
    kospi_list = db_cursor.fetchall()

    keywords = [item[0] for item in kospi_list]
    for keyword in keywords:
        result = news_search(keyword)
        print(result)