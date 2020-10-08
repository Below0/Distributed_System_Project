#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import random
import string
from time import sleep
from kafka import KafkaProducer
import json

string_pool = string.ascii_lowercase + string.digits
company_pool = ["현대자동차","삼성전자","LG전자","네이버","카카오","SK텔레콤"]


with open('./config/db.json') as json_file:
    config_data = json.load(json_file)


addr = [config_data['addr']+':9092']

topicName = 'test'

producer = KafkaProducer(bootstrap_servers=addr,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                        api_version=(0,10))


def make_ID():
    _LENGTH = 10
    result = random.choice(string.ascii_lowercase)
    for i in range(_LENGTH):
        result += random.choice(string_pool)
    return result

def choice_stock():
    return random.choice(company_pool)

def make_log(n):
    log_list = []
    stock = choice_stock()
    
    for i in range(n):
        ID = make_ID()
        
        if n % 2 == 0:
            stock = choice_stock()
            
        log = {
            "id": ID,
            "stock": stock
        }
        
        log_list.append(log)
    
    return log_list


for i in range(5):
    sleep_time = random.randint(1,5)
    cnt = random.randint(9,99)
    log_list = make_log(cnt)
    
    for log in log_list:
        #print(i, log)
        producer.send(topicName, value = log)
    
    sleep(sleep_time)



# In[ ]:




