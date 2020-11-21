from elasticsearch import Elasticsearch, helpers
import os 
import json

elasticsearch_ip = os.getenv('ELASTICSEARCH_HOST','localhost')
elasticsearch_port = os.getenv('ELASTICSEARCH_PORT','9200')

es = Elasticsearch(elasticsearch_ip)
index = "naver.finance.board"

def create_analysis_index():


    
    with open('init_mapping.json', 'r') as f:
        mapping = json.load(f)
    
    es.indices.create(index=index, body=mapping)

   # doc = {
          
    #        "bad":"1",
     #       "body":"1",
      #      "date":"11:11:11",
       #     "good":"1",
        #    "id":"1",
         #   "ip":"1",
          #  "title":"1"
   # }

    
    #es.indices.create(index=index, body=mapping)

      
   # es.index(index="naver.finance.board", doc_type="_doc", body=doc)

    #if es.indices.exists(index=index): # 존재하면 삭제 후 생성
    #    es.indices.delete(index=index);

    #es.indices.create(index=index, body = body, ignore=400)

def all_index():
    print(es.cat.indices())

#try:
create_analysis_index()
all_index()
print("Success, Elasticsearch mapping")

#except:
#    print("Error, Ealsticsearch mapping")
#    pass
