from elasticsearch import Elasticsearch, helpers
import os
import json


elasticsearch_ip = os.getenv('ELASTICSEARCH_HOST','localhost')

es = Elasticsearch(elasticsearch_ip)

def allIndex():
    print(es.cat.indices())

def searchAll():
    print('--')
    res = es.search(
            index = "naver.finance.board",  
            body = {
                "query":{"match_all":{}}
                }
    )
    print(json.dumps(res, ensure_ascii=False, indent = 1))

#동일한 ip중 다른 아이디로 여러 글을 올리는 사람 색출
def find_Same_Ip_Id():
    res = es.search(
            index = "naver.finance.board",  
 
            body = {
                "aggs": {
                    "same_ip_group": {
                        "terms": {
                            "field":"ip.keyword"
                        },
                        "aggs":{
                            "same_id_group": {
                                "terms": {
                                    "field": "title.keyword"
                                    }
                                }
                            }
                        }
                    }
                }
            )
   
    print(json.dumps(res, ensure_ascii=False, indent = 1))
    


#allIndex()
#searchAll()
find_Same_Ip_Id();
