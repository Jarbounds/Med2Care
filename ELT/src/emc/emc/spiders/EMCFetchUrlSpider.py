
import re
import time

from scrapy import Spider
from copy import deepcopy
from scrapy.http import Request, Response


def is_discontinued(medicine_selector) -> bool:
    """
    Utility function for checking if a medicine entry is discontinued
    :param medicine_selector: The selector that contains the medicine result.
    """
    discontinued_selector_list = medicine_selector.css('div.discontinued-info')
    if len(discontinued_selector_list) == 0:
        return False
    for attribute in discontinued_selector_list.attrib.values():
        if 'discontinue' in attribute:
            return True
    return False


class EMCFetchUrlSpider(Spider):
    name: str = 'EMCFetchUrlCrawler'
    allowed_domains: list[str] = ['www.medicines.org.uk']

    def start_requests(self):
        # Request search for obtaining number of results
        emc_search_urls = self.kwargs.get('emc_search_urls')
        for url in emc_search_urls:
            yield Request(url, self.get_num_results, dont_filter=True)
            # time.sleep(self.settings.attributes['DOWNLOAD_DELAY'].value)

    def get_num_results(self, response: Response):
        # Parse response
        span_results = response.css('span.search-results-header-summary-total')
        # span_results: list = [span for span in span_list if span.attrib.get('id', '') == 'SearchResultsPagingView']
        if len(span_results) == 0:
            return
        total_results_span = span_results[0]
        total_results = int(re.findall('[0-9]+', total_results_span.root.text)[0])

        current_offset: int = 1
        limit = self.kwargs.get('limit')
        emc_search_url = response.url

        urls = []

        while True:
            to_search_url = f'{emc_search_url}&offset={current_offset}&limit={limit}&fullText=true'
            urls.append(deepcopy(to_search_url))

            current_offset += limit
            if current_offset > total_results:
                break

        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True)
            # time.sleep(self.settings.attributes['DOWNLOAD_DELAY'].value)

    def parse(self, response: Response, **kwargs):
        results_box = response.css('div.search-results-products-wrapper')
        results = results_box.css('div.search-results-product')
        for result in results:
            if is_discontinued(result):
                continue
            link_list_div = result.css('ul.search-results-product-links')
            links = link_list_div.css('li')
            for link in links:
                text: str = link.css('a::text').get()
                if 'smpc' in text.lower():
                    uri: str = link.css('a::attr(href)').get()
                    yield {
                        'uri': uri
                    }
                    break
