from scrapy import Spider
from scrapy.http import Request, Response


# def is_discontinued(medicine_selector) -> bool:
#     """
#     Utility function for checking if a medicine entry is discontinued
#     :param medicine_selector: The selector that contains the medicine result.
#     """
#     discontinued_selector_list = medicine_selector.css('div.discontinued-info')
#     if len(discontinued_selector_list) == 0:
#         return False
#     for attribute in discontinued_selector_list.attrib.values():
#         if 'discontinue' in attribute:
#             return True
#     return False


class MedicineURLSpider(Spider):
    name: str = 'MedLinePlusFetchUrlCrawler'
    allowed_domains: list[str] = ['www.medlineplus.gov']

    def start_requests(self):
        # Request search for obtaining number of results
        base_url = self.kwargs.get('base_url', None)
        if base_url is not None:
            yield Request(base_url, self.get_medicine_lists, dont_filter=True)

    def get_medicine_lists(self, response: Response):
        base_url = response.url.rsplit('/', 1)[0]
        start_letter_url_list: list = response.css('ul.alpha-links > li > a').xpath('@href').getall()
        start_letter_url_list = [
            f'{base_url}/{url}' for url in start_letter_url_list
        ]
        for url in start_letter_url_list:
            yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response: Response, **kwargs):
        base_url: str = response.url.rsplit('/', 1)[0]
        medicine_url_list: list = response.css('ul[id="index"] > li > a').xpath('@href').getall()
        medicine_url_list = [
            f'{base_url}{url.lstrip(".")}' for url in medicine_url_list
        ]

        for url in medicine_url_list:
            yield {
                'url': url
            }
