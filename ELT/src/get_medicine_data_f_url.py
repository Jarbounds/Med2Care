import requests
from requests import Response
from bs4 import BeautifulSoup, Tag
from medicine_dataclasses import Medicine


default_medicine_url_file: str = '../data/medicines_urls.txt'


def semicolon_separate_excipients(excipients_content: str) -> str:
    excipient_content_parts: list = excipients_content.split('\n\n')
    excipients_list_raw: list = [
            excipients_str
            for i, excipients_str in enumerate(excipient_content_parts) if i % 2 != 0
    ]
    excipients_joined = ''.join(excipients_list_raw)
    excipients_to_return = excipients_joined.replace(' \n', '\n').replace('\n', ';')
    return excipients_to_return


# Todo: Define a semicolon separate incompatibilities function, if seen necessary.
# Todo: Generalize element (information) extraction from beautiful soup.


def main():
    with open(default_medicine_url_file, 'r') as url_files:
        medicine_urls: list = [url.rstrip('\n') for url in url_files.readlines()]

    for medicine_url in medicine_urls:
        response: Response = requests.get(medicine_url)
        soup = BeautifulSoup(response.content, features='html.parser')

        current_medicine: Medicine = Medicine()

        product_info_anchor = soup.find('a', attrs={'id': 'PRODUCTINFO'})
        for elem in product_info_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                medicine_name: str = elem.text.strip('\n')
                current_medicine.metadata.name = medicine_name
                break

        composition_anchor = soup.find('a', attrs={'id': 'COMPOSITION'})
        for elem in composition_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                composition: str = elem.text.strip('\n')
                current_medicine.metadata.composition = composition
                break

        indications_anchor = soup.find('a', attrs={'id': 'INDICATIONS'})
        for elem in indications_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                therapeutic_indications: str = elem.text.strip('\n')
                current_medicine.metadata.clinical_particulars.therapeutic_indications = therapeutic_indications
                break

        contraindications_anchor = soup.find('a', attrs={'id': 'CONTRAINDICATIONS'})
        for elem in contraindications_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                contraindications: str = elem.text.strip('\n')
                # Todo: Structure this as a list (not quite there)
                current_medicine.metadata.clinical_particulars.contraindications.disease.append(contraindications)
                break

        pregnancy_anchor = soup.find('a', attrs={'id': 'PREGNANCY'})
        for elem in pregnancy_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                pregnancy: str = elem.text.strip('\n')
                current_medicine.metadata.clinical_particulars.contraindications.pregnancy = pregnancy
                break

        machine_ops_anchor = soup.find('a', attrs={'id': 'MACHINEOPS'})
        for elem in machine_ops_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                machine_ops: str = elem.text.strip('\n')
                current_medicine.metadata.clinical_particulars.contraindications.machine_ops = machine_ops
                break

        excipients_anchor = soup.find('a', attrs={'id': 'EXCIPIENTS'})
        for elem in excipients_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                excipients: str = elem.text.strip('\n')
                excipients_formatted = semicolon_separate_excipients(excipients)
                current_medicine.metadata.clinical_particulars.contraindications.excipients = excipients_formatted
                break

        incompatibilities_anchor = soup.find('a', attrs={'id': 'INCOMPATIBILITIES'})
        for elem in incompatibilities_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                incompatibilities: str = elem.text.strip('\n')
                current_medicine.metadata.clinical_particulars.contraindications.incompatibilities = incompatibilities
                break

        doc_version_anchor = soup.find('a', attrs={'id': 'DOCREVISION'})
        for elem in doc_version_anchor.next_elements:
            if isinstance(elem, Tag) and 'sectionWrapper' in elem.attrs['class']:
                revision_date: str = elem.text.strip('\n').replace('/', '-')
                current_medicine.metadata.revision_date = revision_date
                break

        # Todo: Save to file (missing the medicine id for complete definition)


if __name__ == '__main__':
    main()
