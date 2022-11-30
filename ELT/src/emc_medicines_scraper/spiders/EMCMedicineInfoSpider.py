import re
from scrapy import Spider
from scrapy.http import Request, HtmlResponse
from bs4 import BeautifulSoup, Tag
from .. import Medicine, Metadata, ClinicalParticulars, ContraIndications


def extract(anchor_id: str, parser: BeautifulSoup, return_element: bool = False) -> str | Tag:
    match = parser.find('a', attrs={'id': anchor_id})
    content_div = match.find_next('div', attrs={'class': 'sectionWrapper'})
    if return_element:
        return content_div
    text = content_div.text.strip()
    return text


class EMCMedicineInfoCrawler(Spider):
    name: str = 'EMCMedicineInfoCrawler'
    allowed_domains: list[str] = ['www.medicines.org.uk']

    def start_requests(self):
        urls_filename = self.kwargs.get('urls_filename', '')
        with open(urls_filename, 'r', encoding='utf-8') as file:
            urls: list[str] = [url.rstrip('\n') for url in file.readlines()]
        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True)

    def __parse_medicine_name(self, parser: BeautifulSoup) -> str:
        medicine_name = extract('PRODUCTINFO', parser)
        return medicine_name

    def __parse_composition(self, parser: BeautifulSoup) -> str:
        composition = extract('COMPOSITION', parser)
        return composition

    def __parse_therapeutic_indications(self, parser: BeautifulSoup) -> str:
        therapeutic_indications = extract('INDICATIONS', parser)
        return therapeutic_indications

    def __parse_disease_contraindications(self, parser: BeautifulSoup) -> list:
        disease_contraindications = extract('CONTRAINDICATIONS', parser).split('\n')
        return disease_contraindications

    # Todo: Problems found here, so much incoherence with this section text... :(
    def __parse_pregnancy_contraindications(self, parser: BeautifulSoup) -> str:
        pregnancy_contraindications = extract('PREGNANCY', parser)
        return pregnancy_contraindications

    def __parse_machine_ops_contraindications(self, parser: BeautifulSoup) -> str:
        machine_ops = extract('MACHINEOPS', parser)
        return machine_ops

    def __parse_excipients(self, parser: BeautifulSoup) -> str:
        excipients = extract('EXCIPIENTS', parser)
        to_rem = [
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
                if rem in excipient.lower():
                    to_add = False
                    break
            if to_add:
                cleaned_excipients.append(excipient)

        joined = ';'.join(cleaned_excipients)
        return joined

    def __parse_incompatibilities(self, parser: BeautifulSoup):
        incompatibilities_list = extract('INCOMPATIBILITIES', parser).split('\n')
        incompatibilities = ';'.join(incompatibilities_list)
        return incompatibilities

    def __parse_contraindications(self, response: HtmlResponse) -> ContraIndications:
        parser = BeautifulSoup(response.body, features='lxml')
        disease_contraindications = self.__parse_disease_contraindications(parser)
        pregnancy_contraindications = self.__parse_pregnancy_contraindications(parser)
        machine_ops_contraindications = self.__parse_machine_ops_contraindications(parser)
        excipients = self.__parse_excipients(parser)
        incompatibilities = self.__parse_incompatibilities(parser)

        contraindications: ContraIndications = ContraIndications(
            disease=disease_contraindications,
            pregnancy=pregnancy_contraindications,
            machine_ops=machine_ops_contraindications,
            excipients=excipients,
            incompatibilities=incompatibilities
        )

        return contraindications

    def __parse_clinical_particulars(self, response: HtmlResponse) -> ClinicalParticulars:
        parser = BeautifulSoup(response.body, features='lxml')
        indications = self.__parse_therapeutic_indications(parser)
        contraindications = self.__parse_contraindications(response)

        clinical_particulars: ClinicalParticulars = ClinicalParticulars(
            therapeutic_indications=indications,
            contraindications=contraindications
        )
        return clinical_particulars

    def __parse_revision_date(self, parser: BeautifulSoup) -> str:
        revision_date = extract('DOCREVISION', parser)
        return revision_date

    def parse(self, response: HtmlResponse, **kwargs):
        parser = BeautifulSoup(response.body, features='lxml')
        medicine_id: str = str(re.findall('[0-9]+', response.url)[0])
        medicine_name = self.__parse_medicine_name(parser)
        composition = self.__parse_composition(parser)
        clinical_particulars = self.__parse_clinical_particulars(response)
        revision_date = self.__parse_revision_date(parser)

        medicine: Medicine = Medicine(
            medicine_id=medicine_id,
            metadata=Metadata(
                name=medicine_name,
                composition=composition,
                clinical_particulars=clinical_particulars,
                revision_date=revision_date
            )
        )

        yield medicine
