import os
from os import listdir
from configparser import ConfigParser
from typing import Any, Callable

from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from emc.emc.spiders import EMCFetchUrlSpider


def configure_and_retrieve_crawler(settings, callback_func: Callable) -> Any:
    fetch_urls_crawler = Crawler(EMCFetchUrlSpider, settings=settings)
    fetch_urls_crawler.signals.connect(callback_func, signal=signals.item_scraped)

    return fetch_urls_crawler


def request_results(process, crawler, request_urls: list[str], limit: int) -> None:
    process.crawl(crawler, kwargs={
        'emc_search_urls': request_urls,
        'base_offset': 1,
        'limit': limit
    })


def main():
    config: ConfigParser = ConfigParser()
    config.read('../../configurations/configurations.ini')

    emc_base_search_url: str = config['URL']['emc_base_search_url']
    emc_base_url: str = config['URL']['emc_base_url']

    atc_codes_dir: str = config['PATH']['atc_codes_dir']
    medicine_urls_file: str = config['PATH']['medicine_urls_file']

    emc_search_filters: str = config['CONSTANTS']['emc_search_filters']
    limit: int = int(config['CONSTANTS']['limit'])

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    medicine_urls: list[str] = []

    atc_codes_by_disease: dict[str, list[str]] = {}

    for disease in listdir(atc_codes_dir):
        with open(os.path.join(atc_codes_dir, disease), 'r', encoding='utf-8') as file:
            atc_codes_by_disease[disease] = [
                atc_code.rstrip('\n') for atc_code in file.readlines()
            ]

    def handle_url_scraped(item: dict):
        medicine_urls.append(f'{emc_base_url}{item["uri"]}')

    fetch_urls_crawler: Crawler = configure_and_retrieve_crawler(settings, handle_url_scraped)
    urls = []

    for atc_code_list in atc_codes_by_disease.values():
        for atc_code in atc_code_list:
            atc_code_query: str = f'q={atc_code}'
            # Show only medicines with health professional information
            healthcare_information_filter_query = f'filters={emc_search_filters}'
            request_url: str = f'{emc_base_search_url}?{atc_code_query}&{healthcare_information_filter_query}'
            urls.append(request_url)

    request_results(process, fetch_urls_crawler, urls, limit)
    process.start()
    process.join()

    # write urls to file
    with open(medicine_urls_file, 'w', encoding='utf-8') as file:
        for url in medicine_urls:
            file.write(f'{url}\n')


if __name__ == '__main__':
    main()
