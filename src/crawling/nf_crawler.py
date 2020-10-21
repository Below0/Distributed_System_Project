import os
import sys
import urllib.request
from urllib.parse import *
import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import json
import re
import json
import datetime
from collections import deque


with open('./config/config.json') as json_file:
    config_data = json.load(json_file)

addr = [config_data['kafka']+':9092']

topic = 'naver.finance.board'

producer = KafkaProducer(bootstrap_servers=addr,
                         value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                        api_version=(0,10))


def remove_tag(content):
    cleanr =re.compile('<.*?>')
    result = re.sub(cleanr, '', content)
    return result
        
def get_bs_obj(url):
    result = requests.get(url, headers={'User-Agent':'Mozilla/5.0'})
    bs_obj = BeautifulSoup(result.content, "html.parser")
    return bs_obj

class roomCrawler:
    
    main_url = 'https://finance.naver.com'
    
    def __init__(self, code = '005930', page = 2): #default code = 삼성전지
        self.room_url = self.main_url+'/item/board.nhn?code='+code
        self.page = page
        

    def detail_crawl(self, link):
        target_link = self.main_url + link
        bs = get_bs_obj(target_link)
        author_text = bs.find("span", class_="gray03").text
        ID, IP = author_text.split(" ")
        ID = ID[:-4] # Erasing Masking
        
        og_date = bs.find("th", class_="gray03 p9 tah").text
        date_obj = datetime.datetime.strptime(og_date, '%Y.%m.%d %H:%M')
        date = date_obj.strftime('%Y-%m-%dT%H:%M:%S')
    
        title = bs.find("strong", class_="p15").text
        body = bs.find("div", id="body").text.replace("\r"," ")
        
        good_cnt = bs.find("strong", class_="_goodCnt").text
        bad_cnt = bs.find("strong", class_="_badCnt").text
        
        post = {
            "id": ID,
            "ip": IP,
            "date" : date,
            "title": title,
            "body": body,
            "good": good_cnt,
            "bad": bad_cnt
        }
        
        return post
        
    def room_crawl(self, page = 1):
        bs = get_bs_obj(self.room_url+'&page='+str(page))
        lst = bs.find_all("td", class_="title")
            
        for i in range(len(lst)-1, 0, -1):
            a = lst[i].find('a')
            link = a.get('href')
            post = self.detail_crawl(link)
            producer.send(topic, value = post)

        
    def run(self):
        self.room_crawl()

if __name__ == "__main__":
    temp = roomCrawler('005930')
    crawl_data = temp.run()
	
