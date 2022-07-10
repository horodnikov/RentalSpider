from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from rentalparser.spiders.tutti import TuttiSpider
from rentalparser import settings


if __name__ == "__main__":
    crawler_setting = Settings()
    crawler_setting.setmodule(settings)

    search = ['bern', 'zurich', 'basel']
    process = CrawlerProcess(settings=crawler_setting)
    process.crawl(TuttiSpider, search=search)

    process.start()
