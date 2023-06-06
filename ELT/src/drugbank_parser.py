import json
from typing import Iterator
from lxml import etree as et
from lxml.etree import Element
from hashlib import sha1
from datetime import date

# Define the DrugBank namespace
ns = {'db': 'http://www.drugbank.ca'}


def preg_ops_from_disease(disease: str):
    return 'NA', 'NA'


def is_drug_start(event: str, elem: Element, started: bool):
    check_tag = '{{{ns}}}drug'.format(ns=ns['db'])
    return not started and event == 'start' and elem.tag == check_tag and is_root_child(elem)


def is_drug_end(event: str, elem: Element, started: bool):
    check_tag = '{{{ns}}}drug'.format(ns=ns['db'])
    return started and event == 'end' and elem.tag == check_tag and is_root_child(elem)


def is_drug_products_start(event: str, elem: Element):
    check_tag = '{{{ns}}}products'.format(ns=ns['db'])
    return event == 'start' and elem.tag == check_tag


def is_drug_id(event: str, elem: Element):
    id_tag = '{{{ns}}}drugbank-id'.format(ns=ns['db'])
    drug_tag = '{{{ns}}}drug'.format(ns=ns['db'])
    drug_bank_tag = '{{{ns}}}drugbank'.format(ns=ns['db'])
    is_id = event == 'end' and elem.tag == id_tag
    if is_id:
        correct_parent = elem.getparent().tag == drug_tag and elem.getparent().getparent().tag == drug_bank_tag
        return is_id and correct_parent
    return is_id


def is_drug_name(event: str, elem: Element):
    name_tag = '{{{ns}}}name'.format(ns=ns['db'])
    drug_tag = '{{{ns}}}drug'.format(ns=ns['db'])
    drug_bank_tag = '{{{ns}}}drugbank'.format(ns=ns['db'])
    is_name = event == 'end' and elem.tag == name_tag
    if is_name:
        correct_parent = elem.getparent().tag == drug_tag and elem.getparent().getparent().tag == drug_bank_tag
        return correct_parent
    return is_name


def is_drug_dosage(event: str, elem: Element):
    dosage_tag = '{{{ns}}}dosage'.format(ns=ns['db'])
    is_dosage = event == 'start' and elem.tag == dosage_tag
    if is_dosage:
        dosages_tag = '{{{ns}}}dosages'.format(ns=ns['db'])
        drug_tag = '{{{ns}}}drug'.format(ns=ns['db'])
        drug_bank_tag = '{{{ns}}}drugbank'.format(ns=ns['db'])
        tags = [dosages_tag, drug_tag, drug_bank_tag]
        p = elem
        for tag in tags:
            p = p.getparent()
            if p.tag != tag:
                return False
        return True
    return False


def is_root_child(element: Element):
    parent = element.getparent()
    if parent is None:
        return False
    grandparent = parent.getparent()
    return grandparent is None


def main():
    drugbank_xml: Iterator = et.iterparse('../data/full_database.xml', events=("start", "end"))

    drug_bank_id: str = ''
    active_principle: str = ''
    name: str = ''
    therapeutic_indications: str = ''
    disease: str = ''
    lab_or_brand_name: str = ''
    drug_or_product_dosage: str = ''
    drug_or_product_strength: str = ''
    pharmaco_dynamics: str = ''
    revision_date: str = ''
    incompatibilities: list = []
    started: bool = False

    # Iterate over the XML and extract information from the interesting tags
    for event, elem in drugbank_xml:
        # We reached a new medicine to be processed
        if is_drug_start(event, elem, started):
            drug_bank_id = ''
            name = ''
            incompatibilities = []
            started = True
            active_principle = ''
            revision_date: str = str(date.today())

        elif is_drug_name(event, elem):
            active_principle = elem.text

        elif event == 'end' and elem.tag == '{http://www.drugbank.ca}toxicity':
            disease = elem.text if elem.text is not None else ''

        elif event == 'end' and elem.tag == '{http://www.drugbank.ca}pharmacodynamics':
            pharmaco_dynamics = elem.text if elem.text is not None else ''

        elif event == 'end' and elem.tag == '{http://www.drugbank.ca}indication':
            therapeutic_indications = elem.text if elem.text is not None else ''

        elif is_drug_products_start(event, elem):
            aux_product = elem.find('db:product', ns)
            if aux_product is None:
                continue
            n = aux_product.findtext('db:name', namespaces=ns)
            d = aux_product.findtext('db:dosage-form', namespaces=ns)
            s = aux_product.findtext('db:strength', namespaces=ns)
            lab_or_brand_name = n if n is not None else ''
            drug_or_product_dosage = d if d is not None else ''
            drug_or_product_strength = s if s is not None else ''

        elif event == 'start' and elem.tag == '{http://www.drugbank.ca}international-brands':
            if lab_or_brand_name:
                continue
            aux_brand = elem.find('db:international-brand', ns)
            if aux_brand is None:
                continue
            n = aux_brand.findtext('db:name', namespaces=ns)
            lab_or_brand_name = n if n is not None else ''

        elif is_drug_dosage(event, elem):
            if drug_or_product_dosage and drug_or_product_strength:
                continue
            f = elem.findtext('db:form', namespaces=ns)
            s = elem.findtext('db:strength', namespaces=ns)
            drug_or_product_dosage = f if f is not None else ''
            drug_or_product_strength = s if s is not None else ''

        elif is_drug_id(event, elem):
            # Extract the drug ID when we encounter the drugbank-id element
            if elem.attrib.get('primary', None) is not None:
                drug_bank_id = elem.text

        # Extract the interaction information when we encounter the drug-interaction element
        elif event == 'end' and elem.tag == '{http://www.drugbank.ca}drug-interaction':
            interaction = {
                'drugbank_id': elem.findtext('db:drugbank-id', namespaces=ns),
                'description': elem.findtext('db:description', namespaces=ns)
            }
            incompatibilities.append(interaction)
        # We ended current medicine processing
        elif is_drug_end(event, elem, started):
            print(f'Processed {drug_bank_id}')
            started = False
            medicine_id = sha1(f'{drug_bank_id}{name}'.encode()).hexdigest()
            pregnancy, machine_ops = preg_ops_from_disease(disease)
            name = ' '.join([lab_or_brand_name, drug_or_product_strength, drug_or_product_dosage])
            composition = ' '.join([drug_or_product_strength, active_principle])

            if not therapeutic_indications:
                elem.clear()
                continue

            medicine_dict = {
                'medicine_id': medicine_id,
                'platform_id': drug_bank_id,
                'metadata': {
                    'name': name,
                    'composition': composition,
                    'clinical_particulars': {
                        'therapeutic_indications': therapeutic_indications,
                        'contraindications': {
                            'disease': disease if disease != '' else 'NA',
                            'pregnancy': pregnancy,
                            'machine_ops': machine_ops,
                            'pharmacodynamics': pharmaco_dynamics if pharmaco_dynamics != '' else 'NA',
                            'excipients': 'NA',
                            'incompatibilities': incompatibilities
                        }
                    },
                    'revision_date': revision_date
                }
            }
            elem.clear()
            with open(f'../data/extracted_medicines/{medicine_id}.json', 'w') as fp:
                fp.write(json.dumps(medicine_dict))


if __name__ == '__main__':
    main()
