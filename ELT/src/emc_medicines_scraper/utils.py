from bs4 import Tag


def check_element_text(element: Tag) -> str:
    if element is None:
        return 'Not Applicable'
    if len(element.text.strip()) > len('Not Applicable'):
        return 'Applicable'
    return 'Not Applicable'
