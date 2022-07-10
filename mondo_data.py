from pymongo import MongoClient

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'tutti_test'

with MongoClient(host=MONGO_HOST, port=MONGO_PORT) as client:
    db = client[DB_NAME]
    # print(db.list_collection_names())
    collection = db['tutti']
    collection.drop()

    for num, value in enumerate(collection.find()):
        print(num, value['characteristics'])
