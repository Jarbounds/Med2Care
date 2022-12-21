from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from emc_medicines_scraper.spiders import EMCMedicineInfoCrawler


DEFAULT_URLS_FILE = '../data/medicines_urls.txt'


def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    medicine_info_crawler = Crawler(EMCMedicineInfoCrawler, settings=settings)

    process.crawl(medicine_info_crawler, kwargs={
        'urls_filename': DEFAULT_URLS_FILE
    })

    process.start()
    process.join()


if __name__ == '__main__':
    main()
