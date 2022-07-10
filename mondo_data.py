from pymongo import MongoClient
import pandas as pd


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'tutti_rental'


def connect_mongo():
    with MongoClient(host=MONGO_HOST, port=MONGO_PORT) as client:
        db = client[DB_NAME]
        collection = db['tutti']
        mongo_list = list(collection.find())
    return mongo_list


def modify_characteristics(upload_list: list):
    for element in upload_list:
        for key, value in element['characteristics'].items():
            element[key] = value
        del element['characteristics']
    return upload_list


def modify_rent(rent_list):
    for element in rent_list:
        if element['Miete CHF'] is not None:
            for key, value in element['Miete CHF'].items():
                element['Miete CHF'] = value
                element['Miete_Zeitraum'] = key
    return rent_list


uploaded_list = connect_mongo()
modify_list = (modify_characteristics(uploaded_list))
result_list = modify_rent(modify_list)

df = pd.DataFrame(result_list)
print()