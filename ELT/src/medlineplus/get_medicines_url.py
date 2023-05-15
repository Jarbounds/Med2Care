import os
from os import listdir
from configparser import ConfigParser
from typing import Any, Callable

from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from medlineplus.spiders import MedicineURLSpider


def configure_and_retrieve_crawler(settings, spider, callback_func: Callable) -> Any:
    fetch_urls_crawler = Crawler(spider, settings=settings)
    fetch_urls_crawler.signals.connect(callback_func, signal=signals.item_scraped)

    return fetch_urls_crawler


def request_results(process, crawler, base_url) -> None:
    process.crawl(crawler, kwargs={
        'base_url': base_url,
    })


def main():
    config: ConfigParser = ConfigParser()
    config.read('../../configurations/configurations.ini')

    med_line_base_url: str = config['URL']['med_line_base_url']
    medicine_urls_file: str = config['PATH']['medicine_urls_file']

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    medicine_urls: set[str] = set()

    def handle_url_scraped(item: dict):
        medicine_urls.add(item['url'])

    fetch_urls_crawler: Crawler = configure_and_retrieve_crawler(settings, MedicineURLSpider, handle_url_scraped)

    request_results(process, fetch_urls_crawler, med_line_base_url)
    process.start()
    process.join()

    # write urls to file
    with open(medicine_urls_file, 'w', encoding='utf-8') as file:
        for url in medicine_urls:
            file.write(f'{url}\n')


if __name__ == '__main__':
    main()
