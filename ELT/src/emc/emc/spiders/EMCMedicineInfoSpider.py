import re

from scrapy import Spider
from scrapy.http import Request, HtmlResponse
from bs4 import BeautifulSoup, Tag
from .. import Medicine, Metadata, ClinicalParticulars, ContraIndications
from .. import check_element_text


def extract(anchor_id: str, parser: BeautifulSoup, return_element: bool = False) -> str | Tag:
    match = parser.find('summary', attrs={'id': anchor_id})
    content_div = match.find_next('div', attrs={'class': 'sectionWrapper'})
    if return_element:
        return content_div
    text: str = ''
    for s in content_div.strings:
        if s.isprintable():
            text = f'{text}\n{s}'
    text = text.strip()
    return text


def parse_medicine_name(parser: BeautifulSoup) -> str:
    medicine_name = extract('PRODUCTINFO', parser)
    return medicine_name


def parse_composition(parser: BeautifulSoup) -> str:
    composition = extract('COMPOSITION', parser)
    if 'excipient'.casefold() in composition.casefold():
        ignore_case = re.compile(re.escape('excipient'), re.IGNORECASE)
        composition = ignore_case.split(composition)[0]
    return composition


def parse_therapeutic_indications(parser: BeautifulSoup) -> str:
    therapeutic_indications = extract('INDICATIONS', parser)
    return therapeutic_indications


def parse_disease_contraindications(parser: BeautifulSoup) -> str:
    disease_contraindications = extract('CONTRAINDICATIONS', parser)
    return disease_contraindications


def parse_pregnancy_contraindications(parser: BeautifulSoup) -> str:
    page_element: Tag = extract('PREGNANCY', parser, True)
    pregnancy_contraindications = check_element_text(page_element)
    return pregnancy_contraindications


def parse_machine_ops_contraindications(parser: BeautifulSoup) -> str:
    page_element: Tag = extract('MACHINEOPS', parser, True)
    machine_ops = check_element_text(page_element)
    return machine_ops


def parse_excipients(parser: BeautifulSoup) -> str:
    excipients = extract('EXCIPIENTS', parser)
    to_rem = [
        'tablet',
        'core',
        'capsule',
        'coating'
    ]
    excipients_list = [
        excipient.strip() for excipient in excipients.split('\n') if len(excipient) != 0
    ]
    cleaned_excipients: list = []
    for excipient in excipients_list:
        to_add: bool = True
        for rem in to_rem:
            if rem.casefold() in excipient.casefold():
                to_add = False
                break
        if to_add:
            excipient = excipient.strip(',')
            cleaned_excipients.append(excipient)

    joined = ';'.join(cleaned_excipients)
    return joined


def parse_incompatibilities(parser: BeautifulSoup):
    incompatibilities_list = extract('INCOMPATIBILITIES', parser).split('\n')
    incompatibilities = ';'.join(incompatibilities_list)
    return incompatibilities


def parse_contraindications(response: HtmlResponse) -> ContraIndications:
    parser = BeautifulSoup(response.body, features='lxml')
    disease_contraindications = parse_disease_contraindications(parser)
    pregnancy_contraindications = parse_pregnancy_contraindications(parser)
    machine_ops_contraindications = parse_machine_ops_contraindications(parser)
    excipients = parse_excipients(parser)
    incompatibilities = parse_incompatibilities(parser)

    contraindications: ContraIndications = ContraIndications(
        disease=disease_contraindications,
        pregnancy=pregnancy_contraindications,
        machine_ops=machine_ops_contraindications,
        excipients=excipients,
        incompatibilities=incompatibilities
    )

    return contraindications


def parse_clinical_particulars(response: HtmlResponse) -> ClinicalParticulars:
    parser = BeautifulSoup(response.body, features='lxml')
    indications = parse_therapeutic_indications(parser)
    contraindications = parse_contraindications(response)

    clinical_particulars: ClinicalParticulars = ClinicalParticulars(
        therapeutic_indications=indications,
        contraindications=contraindications
    )
    return clinical_particulars


def parse_revision_date(parser: BeautifulSoup) -> str:
    revision_date = extract('DOCREVISION', parser)
    return revision_date


class EMCMedicineInfoSpider(Spider):
    name: str = 'EMCMedicineInfoCrawler'
    allowed_domains: list[str] = ['www.medicines.org.uk']

    def start_requests(self):
        urls = self.kwargs.get('urls_list', [])
        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response: HtmlResponse, **kwargs):
        from hashlib import sha1

        parser = BeautifulSoup(response.body, features='lxml')

        medicine_id: str = str(re.findall('[0-9]+', response.url)[0])
        medicine_name = parse_medicine_name(parser)
        composition = parse_composition(parser)
        clinical_particulars = parse_clinical_particulars(response)
        revision_date = parse_revision_date(parser)

        hashed_id = sha1(f'{medicine_id}{revision_date}'.encode()).hexdigest()

        medicine: Medicine = Medicine(
            medicine_id=hashed_id,
            emc_id=medicine_id,
            metadata=Metadata(
                name=medicine_name,
                composition=composition,
                clinical_particulars=clinical_particulars,
                revision_date=revision_date
            )
        )

        yield medicine
