# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import timestring
import re

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'tutti_rental'


class RentalparserPipeline:
    def __init__(self):
        self.client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.client[DB_NAME]

    def process_item(self, item, spider):
        if spider.name == 'tutti':
            item['publication'] = self.str_to_date(item['publication'])
            item['domain'] = item['domain'][0]
            for key, value in item['characteristics'].items():
                if value:
                    if key == 'Miete CHF':
                        match = re.fullmatch(r'(\d+)\S(\d+)\W+(\D+)',
                                             value.strip())
                        if match:
                            item['characteristics'][key] = {
                                match[3]: int(match[1] + match[2])
                                    }
                        else:
                            item['characteristics'][key] = None
                    elif key == 'Fläche':
                        match = re.fullmatch(r'(\d+)(\D+)', value)
                        if match:
                            item['characteristics'][key] = int(match[1])
                    elif key == 'PLZ':
                        item['characteristics'][key] = int(value)
                    elif key == 'Zimmer':
                        item['characteristics'][key] = float(value)
                    else:
                        item['characteristics'][key] = value.strip()
            collection = self.db[spider.name]
            collection.update_one(
                {'link': item['link']}, {"$set": item}, upsert=True)
        return item

    @staticmethod
    def str_to_date(date_string):
        try:
            if date_string:
                return timestring.Date(f'{date_string}').date
        except timestring.TimestringInvalid:
            pass
