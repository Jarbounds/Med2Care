from typing import Any


def get_member_recursive(doc: dict, member: str) -> Any:
    if member in doc:
        return doc[member]
    for key in doc.keys():
        item = doc[key]
        if isinstance(item, dict):
            value = get_member_recursive(item, member)
            if value:
                return value
    return ''


def json_entities(original):
    try:
        entities_json: dict = {
            'medicine_id': original['medicine_id'],
            'name': original['metadata']['name'],
            'composition': [],
            'therapeutic_indications': [],
            'disease': [],
            'pregnancy': [],
            'machine_ops': [],
            'excipients': [],
            'incompatibilities': [],
            'revision_date': original['metadata']['revision_date']
        }
        return entities_json
    except:
        print(original)


def get_member_lexicon_relations() -> dict:
    chebi_lexicon = 'chebi'
    disease_lexicon = 'do'
    lexicons_relations = {
        'composition': [chebi_lexicon],
        'therapeutic_indications': [disease_lexicon],
        'disease': [disease_lexicon],
        'pharmacodynamics': [disease_lexicon],
        'excipients': [chebi_lexicon],
        'incompatibilities': [chebi_lexicon]
    }
    return lexicons_relations
