from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from emc_medicines_scraper.spiders import EMCFetchUrlCrawler

DEFAULT_EXPORT_FILE = '../data/medicines_urls.txt'
MAX_RESULT_SIZE = 200

medicine_urls: list = []

# EMC base page url
medicines_base_url: str = 'https://www.medicines.org.uk'


def handle_url_scraped(item: dict):
    medicine_urls.append(f'{medicines_base_url}{item["url"]}')


def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    fetch_urls_crawler = Crawler(EMCFetchUrlCrawler, settings=settings)
    fetch_urls_crawler.signals.connect(handle_url_scraped, signal=signals.item_scraped)

    # EMC base search url
    emc_base_search_url: str = f'{medicines_base_url}/emc/search'
    # Define the partial ATC Code for searching medicines (in this case for HIV)
    # Todo: Could be generalized to receive this ATC Code from script argument.
    partial_atc_code_query: str = 'q=J05AF'
    # Show only medicines with health professional information
    healthcare_information_filter_query = 'filters=attributes[spc]'

    process.crawl(fetch_urls_crawler, kwargs={
        'emc_search_url': f'{emc_base_search_url}?{partial_atc_code_query}&{healthcare_information_filter_query}',
        'base_offset': 1,
        'limit': 200,
        'excluded_acs': [
            'entecavir',
            'telbivudine'
        ]
    })

    process.start()
    process.join()

    # write urls to file
    with open(DEFAULT_EXPORT_FILE, 'w', encoding='utf-8') as file:
        for url in medicine_urls:
            file.write(f'{url}\n')


if __name__ == '__main__':
    main()
