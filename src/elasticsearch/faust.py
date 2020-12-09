import faust
import json
import math
import re
import requests
import numpy as np
from elasticsearch import Elasticsearch, helpers
from ast import literal_eval
import os
from datetime import datetime
import redis


elasticsearch_ip = os.getenv('ELASTICSEARCH_HOST','localhost')

es = Elasticsearch(elasticsearch_ip)

app = faust.App('nf-board-11', broker='kafka://49.50.174.75:9092', broker_max_poll_record=3)

#redis = redis.Redis(host='localhost', port=6379, db=0)

class Message(faust.Record):
    date: str
    collected_at: str
    id: str
    ip: str
    title: str
    body: str
    good: int
    bad: int
    is_reply: int
    emotion: int = 0
    positive_score: float = 0.0
    normal_score: float = 0.0
    negative_score: float = 0.0
 
def analyze_nori(date, tmp_id, tmp_ip, tmp_title, tmp_body):
    tmp = es.search(
        index = 'nori_test',
            body = {
                "query" : {
                    "bool":{
                        "filter":[
                            {"match": {"date": date}},
                            {"match": {"id": tmp_id}},
                            {"match": {"ip": tmp_ip}},
                            {"match": {"title": tmp_title}},
                            {"match": {"body": tmp_body}}
                            ]
                        }
                }
            }
    )
    # print(tmp['hits'])
    if tmp['hits']['total']['value']!=0:
        return
    else:
        res = indices_client.analyze(index = "nori_test",
        body={
            "analyzer": "nori_analyzer",
            "text": str(tmp_title+tmp_body)
        })
        token_list = [res['tokens'][x]['token'] for x in range(len(res['tokens']))]
        for token in token_list:
            if len(token)>1:
                result = es.index(index = 'nori_test', body = {

                            "tokenlist" : token,
                            "date": date,
                            "id":tmp_id,
                            "ip":tmp_ip,
                            "title":tmp_title,
                            "body":tmp_body

                        })

def check_abuse_list(uid):
    if redis.exists(uid):
        return False
    else:
        redis.set(uid, 0, timedelta(hours=1))
        return True


def utc_time():  
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def make_abuse_query(uid, uip,atype, score):
    if atype == 1:
        msg = "도배 의심"
    elif atype == -1:
        msg = "테스트"
    elif atype == 2:
        msg = "도배(다중 계정) 의심"

    
    query = {
            "id":uid,
            "date":utc_time(),
            "msg":msg,
            "abuse_type":atype,
            "ip":uip,
            "score":score
            }
    print(query)
    return query

def indexing_query(msg):
    res = msg.asdict()
    res['content'] = msg.title +' '+ msg.body
    es.index(index = 'naver.finance.board', body = res)


def update_suspicious_score(msg):
    title_check = es.search(
            index = 'naver.finance.board',
            body = {
                "min_score": 17,
                "query" : {
                    "bool":{
                        "must":{
                            "match":{
                                "title" : msg.title
                                }
                            },
                    "filter":{
                        "term":{"is_reply":0}
                        }
                    }
                    },
                "size" : 100
                }
                
            )

    body_check = es.search(
            index = 'naver.finance.board',
            body = {
                "min_score": 20,
                "query" : {
                    "bool":{
                        "must":{
                            "match":{
                                "title" : msg.body
                                }
                            },
                    "filter":{
                        "term":{"is_reply":0}
                        }
                    }
                    },
                "size" : 100
                }
            )

    same_ipid = 0.0
    diff_ipid = 0.0
    user_name = msg.id
    
    for document in [x['_source'] for x in title_check['hits']['hits']]:

        if document['ip'] == msg.ip and document['id'] == user_name:
            same_ipid += 0.05
        elif document['ip'] == msg.ip and document['id'] != user_name:
            diff_ipid += 0.1

    for document in [x['_source'] for x in body_check['hits']['hits']]:
        if document['ip'] == msg.ip and document['id'] == user_name:
            same_ipid += 0.01
        elif document['ip'] == msg.ip and document['id'] != user_name:
            diff_ipid += 0.25
            
   # now_score = get_abuse_score(user_name) + same_ipid + diff_ipid
    update_score(user_name,msg.ip,same_ipid, diff_ipid)
    
    #if now_score > 1.0:
     #   print(now_score)
  #     register_abuse_list(uid, score)


def get_abuse_score(uid):
    query = {
            "query": {
                "bool": {
                    "filter":{
                        "term":{"id":uid}
                          }
                    }
                },
            "aggs":{
                "total_score": {
                    "sum": {"field":"score"}
                    }
                },
            "size":0
            }

        
    data = es.search(index = 'naver.abusing.list',body = query)
    try:
        score = data['aggregations']['total_score']['value']
    except Exception as err:
        score = 0
    return score


def update_score(uid, uip, same_score, diff_score):
    if same_score > 0.0:
        res = es.index(index = 'naver.abusing.list', body = make_abuse_query(uid,uip,1,same_score))
        print(res)
    if diff_score > 0.0:
        res = es.index(index = 'naver.abusing.list', body = make_abuse_query(uid,uip,2,diff_score))
        print(res)


def register_abuse_list(uid, score):
    if not check_abuse_list(uid):
        return
    
    query = {
            "id":uid,
            "date":utc_time(),
            "score":score
            }

    es.index(index = 'score.abusing.board', body = query)


   
nf_topic = app.topic('naver.finance.board.second', value_type=Message)
target_topic = app.topic('naver.finance.board', value_type=Message)
target_url = "http://118.67.133.179:8888/target"

@app.agent(nf_topic)
async def finance_board(messages):
    async for msg in messages:
        update_suspicious_score(msg)
#        analyze_nori(msg.date, msg.id, msg.ip, msg.title, msg.body)
        indexing_query(msg)
    #    res = msg.asdict()
    #    requests.post(target_url, json=res)
       

if __name__ == '__main__':
    app.main()
