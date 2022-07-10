import scrapy
from scrapy.http import HtmlResponse
from rentalparser.items import RentalparserItem


class TuttiSpider(scrapy.Spider):
    name = 'tutti'
    allowed_domains = ['tutti.ch']

    def __init__(self, search):
        super(TuttiSpider, self).__init__()
        self.start_urls = [
            f'https://www.tutti.ch/de/immobilien/objekttyp/wohnungen,hauser/standort/ort-{location}/typ/mieten?paging=1'
            for location in search]

    def parse(self, response: HtmlResponse):
        rental_links = response.xpath(
            '//div[contains(@id, "item")]/a[contains(@class, "css")]/@href'
            ).getall()
        for link in rental_links:
            yield response.follow(link, callback=self.parse_rental_items)

        url_items = response.url.split('=')
        current_page = int(url_items[-1])
        pagination_arrow_class = response.xpath(
            '//ul[contains(@class, "MuiPagination")]/li[position() = last()]/button/@class').get()

        if 'disabled' not in pagination_arrow_class:
            yield response.follow(f"{url_items[0]}={current_page + 1}",
                                  callback=self.parse)

    def parse_rental_items(self, response: HtmlResponse):
        link = response.url
        domain = self.allowed_domains
        title = response.xpath('//h1[contains(@class, "")]/text()').get()
        publication = response.xpath(
            '//div[contains(@class, "9mKtt pRm6L")]//text()').get()
        characteristics_div = response.xpath(
            '//div[contains(@class,"MuiBox-root css-xdf4mo")]')
        characteristics = {}
        for item in characteristics_div:
            characteristics[item.xpath('.//dt//text()').get()] = item.xpath(
                './/dd//text()').get()
        place_type = response.xpath(
            '//div[contains(@class, "MuiBox-root css-8uhtka")]/a//text()').get()
        yield RentalparserItem(link=link, domain=domain, title=title,
                               publication=publication, place_type=place_type,
                               characteristics=characteristics)
