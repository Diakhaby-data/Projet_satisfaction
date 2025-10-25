from fastapi import FastAPI
import pymysql
from pymongo import MongoClient
from elasticsearch import Elasticsearch

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, world! FastAPI tourne bien dans Docker !"}


@app.get("/mysql-test")
def mysql_test():
    try:
        conn = pymysql.connect(
            host="satis_mysql",  # nom du service docker-compose
            user="root",
            password="rootpassword",
            database="mysql",
            port=3306
        )
        conn.close()
        return {"mysql": "Connexion réussie"}
    except Exception as e:
        return {"mysql": f"Erreur : {str(e)}"}


@app.get("/mongo-test")
def mongo_test():
    try:
        client = MongoClient("mongodb://satis_mongo:27017/")
        dbs = client.list_database_names()
        return {"mongo": f"Connexion réussie, DBs : {dbs}"}
    except Exception as e:
        return {"mongo": f"Erreur : {str(e)}"}


@app.get("/es-test")
def es_test():
    try:
        es = Elasticsearch(["http://satis_elasticsearch:9200"])
        info = es.info()
        return {"elasticsearch": f"Connexion réussie, version {info['version']['number']}"}
    except Exception as e:
        return {"elasticsearch": f"Erreur : {str(e)}"}
