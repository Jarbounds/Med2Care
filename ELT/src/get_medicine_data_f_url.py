import re
from Utils.utils import verify_word

import jsonpickle
import requests
from requests import Response
from bs4 import BeautifulSoup, Tag, NavigableString
from medicine_dataclasses import Medicine, Pregnancy

default_medicine_url_file: str = '../data/medicines_urls.txt'


# known_excipient_headers: list = ['tablet coating', 'tablet core']


def semicolon_separate_excipients(excipients_tag: Tag) -> str:
    excipients_list: list = []
    for child in excipients_tag.children:
        if isinstance(child, Tag):
            for grand_child in child.children:
                if isinstance(grand_child, NavigableString) and grand_child.isprintable():
                    string: str = grand_child.text.strip()
                    excipients_list.append(string)

    to_ret = ';'.join(excipients_list)
    return to_ret


def process_preg_contraind(pregnancy_div: Tag) -> list[Pregnancy]:
    # Separate pregnancy contraindications (fertility, pregnancy, lactation and others), if they exist
    # Todo: See if the 'others' cannot fall in the pregnancy together instead of another object
    names_descriptions: dict[str, str] = {}
    current_description: str = ''
    current_name: str = ''
    for child in pregnancy_div.children:
        if not isinstance(child, Tag):
            continue

        is_first_title: bool = True
        for tag_child in child.children:
            if isinstance(tag_child, Tag):
                # is a name
                if tag_child.name in ['i', 'u', 'b'] and is_first_title:
                    if len(current_description) != 0:
                        names_descriptions[current_name] = current_description.strip()
                        current_description = ''
                    current_name = tag_child.text
                    is_first_title = False
                elif not is_first_title:
                    current_description = f'{current_description} {tag_child.text.strip()}'
            elif isinstance(tag_child, NavigableString) and tag_child.isprintable():
                if is_first_title:
                    current_description = f'{current_description}\n{tag_child.text.strip()}'
                else:
                    current_description = f'{current_description} {tag_child.text.strip()}'

    if len(current_description) != 0:
        names_descriptions[current_name] = current_description.strip()

    # Process lists to Pregnancy objects
    pregnancy_contraindications: list = [
        Pregnancy(name, description) for name, description in names_descriptions.items()
    ]

    return pregnancy_contraindications


# Todo: Define a semicolon separate incompatibilities function, if seen necessary.
# Todo: Generalize element (information) extraction from beautiful soup.


def main():
    with open(default_medicine_url_file, 'r', encoding='utf-8') as url_files:
        medicine_urls: list = [url.rstrip('\n') for url in url_files.readlines()]

    for medicine_url in medicine_urls:
        response: Response = requests.get(medicine_url)
        soup = BeautifulSoup(response.content, features='html.parser')
        medicine_id: str = re.findall("[0-9]+", medicine_url)[0]

        current_medicine: Medicine = Medicine()
        current_medicine.medicine_id = medicine_id

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
                pregnancy_contraindications: list[Pregnancy] = process_preg_contraind(elem)
                current_medicine.metadata.clinical_particulars.contraindications.pregnancy = pregnancy_contraindications
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
                excipients_formatted: str = semicolon_separate_excipients(elem)
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

        print(f'Writing file with id:{medicine_id}')
        # Todo: Save to file (missing the medicine id for complete definition)
        with open(f'../data/json/{medicine_id}.json', 'w', encoding='utf-8') as file:
            file.write(jsonpickle.encode(current_medicine, unpicklable=False, indent=4))


if __name__ == '__main__':
    main()
