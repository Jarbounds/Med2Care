import re
from scrapy import Spider
from scrapy.http import Request, HtmlResponse
from hashlib import sha1


def remove_html_tags(element_content: str) -> str:
    new_element_content = re.sub("<[^>]*>", "", element_content)
    return new_element_content


def find_date(response: HtmlResponse, css_exp: str, regex_exp: str) -> str | None:
    text_list = response.css(css_exp).getall()
    date_str = ''
    for text in text_list:
        for date in re.finditer(regex_exp, text):
            date_str = date.group()
    return date_str if len(date_str) > 0 else None


def extract_details(response: HtmlResponse, id_str: str) -> str:
    text_list = response.css(f'div#{id_str} > .section-body > *').getall()
    concat_text = ' '.join(text_list)
    extracted_text = remove_html_tags(concat_text)
    return extracted_text


def parse_composition(response: HtmlResponse) -> str:
    composition = response.css('div.page-title > h1.with-also::text').get()
    return composition


def parse_therapeutic_indications(response: HtmlResponse) -> str:
    therapeutic_indications = extract_details(response, 'why')
    return therapeutic_indications


def parse_contraindications(response: HtmlResponse) -> str:
    contraindications = extract_details(response, 'precautions')
    return contraindications


def parse_revision_date(response: HtmlResponse) -> str:
    revision_date = find_date(response, 'span', '[0-9]{2}/[0-9]{2}/[0-9]{4}')
    if revision_date is None:
        revision_date = find_date(response, 'article::text', '[0-9]{2}/[0-9]{2}/[0-9]{4}')
    if revision_date is None:
        print('Revision date still None')
    return revision_date


class MedicineInfoSpider(Spider):
    name: str = 'MedlineMedicineInfoCrawler'
    allowed_domains: list[str] = ['medlineplus.gov']

    def start_requests(self):
        urls = self.kwargs.get('urls_list', [])
        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response: HtmlResponse, **kwargs):
        platform_id: str = response.url.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        composition = parse_composition(response)
        medicine_name = composition
        indications = parse_therapeutic_indications(response)
        contraindications = parse_contraindications(response)
        revision_date = parse_revision_date(response)

        hashed_id = sha1(f'{platform_id}{revision_date}'.encode()).hexdigest()

        medicine = {
            'medicine_id': hashed_id,
            'platform_id': platform_id,
            'metadata': {
                'name': medicine_name,
                'composition': composition,
                'therapeutic_indications': indications,
                'contraindications': contraindications,
                'revision_date': revision_date
            }
        }

        yield medicine
