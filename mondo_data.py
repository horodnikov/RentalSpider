from pymongo import MongoClient
import translators as ts
import pandas as pd
from geopy.geocoders import Nominatim
from shapely.geometry import Point

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'tutti_rental'


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


def geo_point(data_frame, field):
    geolocator = Nominatim(user_agent=USER_AGENT)

    address_list = []
    geo_list = []
    for address in set(data_frame[field]):
        if address is not None and not (pd.isnull(address)) is True:
            try:
                geo = geolocator.geocode(address)
                point = Point(float(geo.raw.get("lat")),
                              float(geo.raw.get("lon")))
                address_list.append(address)
                geo_list.append(point)
            except Exception as exception:
                print(exception)
    return pd.DataFrame(data={field: address_list, f'geo_{field}': geo_list})


def is_geo(point_one, point_two):
    try:
        search = point_one.distance(point_two)
        return search
    except AttributeError:
        return False


def distance_geo(data_frame):
    distance = []
    for point in range(len(data_frame['geo_address'])):
        if data_frame['geo_address'][point] and data_frame['geo_location'][point]:
            points_distance = is_geo(data_frame['geo_address'][point], data_frame['geo_location'][point])
            distance.append(points_distance)
        else:
            distance.append(None)
    print(len(distance))
    data_frame['distance'] = distance
    return data_frame


def rename_column(data_frame):
    header_list = []
    for field in data_frame.keys():
        field_en = ts.google(field, from_language='de', to_language='en')
        header_list.append(field_en)

    rename_dict = {}
    for key, value in zip(data_frame.keys(), header_list):
        rename_dict[key] = value
    return data_frame.rename(columns=rename_dict)


def translate_values(data_frame, field):
    translate_dict = {}
    for element in set(data_frame[field]):
        element_en = ts.google(element, from_language='de', to_language='en')
        translate_dict[element] = element_en

    for item in data_frame[field]:
        if item in translate_dict.keys():
            data_frame[field] = translate_dict[item]
    return data_frame


if __name__ == "__main__":
    with MongoClient(host=MONGO_HOST, port=MONGO_PORT) as client:
        db = client[DB_NAME]
        collection = db['tutti']
        uploaded_list = list(collection.find())

        modify_list = (modify_characteristics(uploaded_list))
        result_list = modify_rent(modify_list)

        df = pd.DataFrame(result_list)
        df = rename_column(df)

        pd.set_option('display.max_columns', None)

        df = translate_values(df, 'place_type')
        df_address = geo_point(df, 'address')
        df_merge = pd.merge(df, df_address, on='address', how='left')
        df_city = geo_point(df_merge, 'location')
        df_merge = pd.merge(df_merge, df_city, on='location', how='left')
        df_result = distance_geo(df_merge)

        df_result.to_excel(r'rental.xlsx', sheet_name='rental', index=False)
        data = df_result.to_dict(orient='records')

