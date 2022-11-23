
import re
from scrapy import Spider
from copy import deepcopy
from scrapy.http import Request, Response


def is_discontinued(medicine_selector) -> bool:
    r"""
    Utility function for checking if a medicine entry is discontinued
    :param medicine_selector: The selector that contains the medicine result.
    """
    icon_selector_list = medicine_selector.css('img')
    if len(icon_selector_list) == 0:
        return False
    for attribute in icon_selector_list.attrib.values():
        if 'discontinue' in attribute:
            return True
    return False


class EMCFetchUrlCrawler(Spider):
    name: str = 'EMCFetchUrlCrawler'
    allowed_domains: list[str] = ['www.medicines.org.uk']

    def start_requests(self):
        # Request search for obtaining number of results
        emc_search_url = self.kwargs.get('emc_search_url')
        yield Request(emc_search_url, self.get_num_results, dont_filter=True)

    def get_num_results(self, response: Response):
        # Parse response
        span_list = response.css('span')
        total_results_span = [span for span in span_list if span.attrib.get('id', '') == 'SearchResultsPagingView'][0]
        total_results = int(re.findall('[0-9]+', total_results_span.root.text)[0])

        current_offset: int = 1
        limit = self.kwargs.get('limit')
        emc_search_url = self.kwargs.get('emc_search_url')

        urls = []

        while True:
            to_search_url = f'{emc_search_url}&offset={current_offset}&limit={limit}&fullText=true'
            urls.append(deepcopy(to_search_url))

            current_offset += limit
            if current_offset > total_results:
                break

        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response: Response, **kwargs):
        results_box = response.css('div.search-results')
        results = results_box.css('div.data-row')
        for result in results:
            if is_discontinued(result):
                continue
            link_list_div = result.css('div.col-sm-3')[0]
            link_list = link_list_div.css('ul')[0]
            links = link_list.css('li')
            for link in links:
                text: str = link.css('a::text').get()
                if text.lower() == 'smpc':
                    yield {
                        'url': link.css('a::attr(href)').get()
                    }
                    break
