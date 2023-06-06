import os
from configparser import ConfigParser
from utils.utils import load_from_file_lines
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from medlineplus.spiders import MedicineInfoSpider


def main():
    config: ConfigParser = ConfigParser()
    config.read('../../configurations/configurations.ini')

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    medicine_info_crawler = Crawler(MedicineInfoSpider, settings=settings)

    urls_file: str = config['PATH']['medicine_urls_file_medlineplus']
    output_dir: str = config['PATH']['extracted_medicines_dir']

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    urls = load_from_file_lines(urls_file)

    process.crawl(medicine_info_crawler, kwargs={
        'urls_list': urls,
        'output_dir': output_dir
    })
    process.start()
    process.join()


if __name__ == '__main__':
    main()
