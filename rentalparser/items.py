# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RentalparserItem(scrapy.Item):
    _id = scrapy.Field()
    link = scrapy.Field()
    domain = scrapy.Field()
    title = scrapy.Field()
    publication = scrapy.Field()
    place_type = scrapy.Field()
    characteristics = scrapy.Field()
