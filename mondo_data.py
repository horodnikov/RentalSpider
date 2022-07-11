from pymongo import MongoClient
import translators as ts
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


def modify_rent(rent_list: list):
    for element in rent_list:
        if element['Miete CHF'] is not None:
            for key, value in element['Miete CHF'].items():
                element['Miete CHF'] = value
                element['Zeitraum'] = key
    return rent_list


def rename_column(data_frame):
    header_list = []
    for field in data_frame.keys():
        field_en = ts.google(field, from_language='de', to_language='en')
        header_list.append(field_en)

    rename_dict = {}
    for key, value in zip(data_frame.keys(), header_list):
        rename_dict[key] = value
    return data_frame.rename(columns=rename_dict)


def translate_field(data_frame, field):
    translate_dict = {}
    for element in set(data_frame[field]):
        element_en = ts.google(element, from_language='de', to_language='en')
        translate_dict[element] = element_en

    for item in data_frame[field]:
        if item in translate_dict.keys():
            data_frame[field] = translate_dict[item]
    return data_frame


uploaded_list = connect_mongo()
modify_list = (modify_characteristics(uploaded_list))
result_list = modify_rent(modify_list)

df = pd.DataFrame(result_list)
df = rename_column(df)
df = translate_field(df, 'place_type')

pd.set_option('display.max_columns', None)
df.to_excel(r'rental.xlsx', sheet_name='rental', index=False)
