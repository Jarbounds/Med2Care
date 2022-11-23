import re
from scrapy import Spider, Selector
from scrapy.http import Request, HtmlResponse
from .. import Medicine, Metadata, ClinicalParticulars, ContraIndications, Pregnancy


class EMCMedicineInfoCrawler(Spider):
    name: str = 'EMCMedicineInfoCrawler'
    allowed_domains: list[str] = ['www.medicines.org.uk']

    def start_requests(self):
        urls_filename = self.kwargs.get('urls_filename', '')
        with open(urls_filename, 'r', encoding='utf-8') as file:
            urls: list[str] = [url.rstrip('\n') for url in file.readlines()]
        for url in urls:
            yield Request(url, callback=self.parse, dont_filter=True)

    def __parse_medicine_name(self, response: HtmlResponse) -> str:
        # Get selector for HTML element that contains the medicine name
        medicine_name_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[3]')
        # Gets the medicine name from selector
        medicine_name = medicine_name_selector.css('p::text').get()
        return medicine_name

    def __parse_composition(self, response: HtmlResponse) -> str:
        # Get selector for HTML element that contains the composition
        composition_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[5]')
        # Gets the composition from selector
        composition = composition_selector.css('p::text').get()
        return composition

    def __parse_therapeutic_indications(self, response: HtmlResponse) -> str:
        # Get selector for HTML element that contains the therapeutic indications
        therapeutic_indications_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[11]')
        # Gets the therapeutic indications from selector
        therapeutic_indications_list: list[str] = [
            indication.get() for indication in therapeutic_indications_selector.css('p::text')
        ]
        # Converts to single str
        therapeutic_indications: str = '\n'.join(therapeutic_indications_list)
        return therapeutic_indications

    # TODO: If there are more paragraphs here see how to process
    def __parse_disease_contraindications(self, response: HtmlResponse) -> list:
        # Gets selector for HTML element that contains the contraindications associated with disease
        disease_contraindications_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[15]')
        # Gets the disease contraindications from selector
        disease_contraindications: list = [dc.get() for dc in disease_contraindications_selector.css('p::text')]
        return disease_contraindications

    def __parse_pregnancy_contraindications(self, response: HtmlResponse) -> list[Pregnancy]:
        # Gets selector for HTML element that contains the pregnancy contraindications
        pregnancy_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[21]')
        # Gets the pregnancy condition names from selector
        names = [name.get().strip() for name in pregnancy_selector.css('u::text,i::text,b::text')]
        # Gets the pregnancy condition descriptions from selector
        descriptions = [description.get() for description in pregnancy_selector.css('p::text')]

        current_description = ''
        current_index = 0
        pregnancy_list: list[Pregnancy] = []
        # Parse all the names and descriptions into a dict
        for name in names:
            current_description = ''
            for i in range(current_index, len(descriptions)):
                if not descriptions[i].isprintable():
                    if len(current_description) != 0:
                        pregnancy_list.append(
                            Pregnancy(
                                name=name,
                                description=current_description.strip()
                            )
                        )
                        current_index = i
                        break
                else:
                    current_description = f'{current_description}\n{descriptions[i]}'
        if len(current_description) != 0:
            pregnancy_list.append(
                Pregnancy(
                    name=names[-1],
                    description=current_description.strip()
                )
            )
        return pregnancy_list

    def __parse_machine_ops_contraindications(self, response: HtmlResponse) -> str:
        # Gets selector for HTML element that contains the machine ops contraindications
        machine_ops_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[23]')
        # Gets machine ops contraindications from selector
        machine_ops_list: list = [
            machine_op.get().strip() for machine_op in machine_ops_selector.css('p::text')
        ]
        # Converts to single str
        machine_ops: str = '\n'.join(machine_ops_list)
        return machine_ops

    def __parse_excipients(self, response: HtmlResponse) -> str:
        # Gets selector for HTML element that contains the excipients
        excipient_selector = response.xpath('//*[@id="smpc"]/main/div/div/div[39]')
        # Gets excipients from selector
        excipients_list: list = [
            excipient.get() for excipient in filter(
                lambda ex: ex.get().isprintable(), excipient_selector.css('p::text')
            )
        ]
        excipients: str = ';'.join(excipients_list)
        return excipients

    def __parse_incompatibilities(self, response: HtmlResponse):
        incompatibilities_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[41]')
        incompatibilities_list: list = [
            incompatibility.get() for incompatibility in incompatibilities_selector.css('p::text')
        ]
        incompatibilities: str = ';'.join(incompatibilities_list)
        return incompatibilities

    def __parse_contraindications(self, response: HtmlResponse) -> ContraIndications:
        disease_contraindications = self.__parse_disease_contraindications(response)
        pregnancy_contraindications = self.__parse_pregnancy_contraindications(response)
        machine_ops_contraindications = self.__parse_machine_ops_contraindications(response)
        excipients = self.__parse_excipients(response)
        incompatibilities = self.__parse_incompatibilities(response)

        contraindications: ContraIndications = ContraIndications(
            disease=disease_contraindications,
            pregnancy=pregnancy_contraindications,
            machine_ops=machine_ops_contraindications,
            excipients=excipients,
            incompatibilities=incompatibilities
        )

        return contraindications

    def __parse_clinical_particulars(self, response: HtmlResponse) -> ClinicalParticulars:
        indications = self.__parse_therapeutic_indications(response)
        contraindications = self.__parse_contraindications(response)

        clinical_particulars: ClinicalParticulars = ClinicalParticulars(
            therapeutic_indications=indications,
            contraindications=contraindications
        )
        return clinical_particulars

    def __parse_revision_date(self, response: HtmlResponse) -> str:
        # Gets selector for HTML element that contains the revision_date
        revision_date_selector: Selector = response.xpath('//*[@id="smpc"]/main/div/div/div[57]')
        # Gets the revision date from selector
        revision_date = revision_date_selector.css('p::text').get().strip().replace('/', '-')
        return revision_date

    def parse(self, response: HtmlResponse, **kwargs):
        medicine_id: str = str(re.findall('[0-9]+', response.request.url)[0])
        medicine_name = self.__parse_medicine_name(response)
        composition = self.__parse_composition(response)
        clinical_particulars = self.__parse_clinical_particulars(response)
        revision_date = self.__parse_revision_date(response)

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
