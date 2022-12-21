def get_member_recursive(doc: dict, member: str) -> str:
    if member in doc:
        return doc[member]
    for key in doc.keys():
        item = doc[key]
        if isinstance(item, dict):
            value = get_member_recursive(item, member)
            if value:
                return value
    return ''


# json_doc: dict = {
#     'key1': 'value1',
#     'key2': 'value2',
#     'key3': {
#         'key3_1': 'value3_1',
#         'key3_2': 'value3_2',
#         'key3_3': 'value3_3',
#         'key3_4': 'value3_4',
#     },
#     'key4': 'value4',
#     'key5': 'value5',
# }

# result = get_member_recursive(json_doc, 'key3_5')
# print(result)
