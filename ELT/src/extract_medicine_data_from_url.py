import os
from configparser import ConfigParser

from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from emc_medicines_scraper.spiders import EMCMedicineInfoCrawler


def main():
    config: ConfigParser = ConfigParser()
    config.read('../configurations/config.ini')

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    medicine_info_crawler = Crawler(EMCMedicineInfoCrawler, settings=settings)

    urls_file: str = config['PATH']['medicine_urls_file']
    output_dir: str = config['PATH']['extracted_medicines_dir']

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    process.crawl(medicine_info_crawler, kwargs={
        'urls_file': urls_file,
        'output_dir': output_dir
    })

    process.start()
    process.join()


if __name__ == '__main__':
    main()
