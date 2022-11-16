import requests
from bs4 import BeautifulSoup, Tag
from requests import Response

SmPC_str: str = 'SmPC'
default_export_file = '../data/medicines_urls.txt'

medicine_urls: list = []


def is_discontinued(medicine_result_element: Tag) -> bool:
    r"""
    Utility function for checking if a medicine entry is discontinued
    :param medicine_result_element: The Tag element that contains the medicine result.
    """
    discontinued_icon_element = medicine_result_element.find(name='img')
    if discontinued_icon_element is None:
        return False
    for attribute in discontinued_icon_element.attrs.values():
        if 'discontinue' in attribute:
            return True
    return False


def iterate_search_results(search_results, base_link: str):
    for result in search_results:
        # Check if medicine is discontinued
        if is_discontinued(result):
            continue
        # Find all the 'a' tags
        a_tags = result.findAll(name='a')
        # Filter tags to find the one that has the Summary of Product Characteristics (SmPC) aka Medicine Information
        a_tags_filtered = list(filter(lambda a_tag: a_tag.string == SmPC_str, a_tags))
        # If a SmPC 'a' tag is found
        if len(a_tags_filtered) != 0:
            # Extract the href attribute
            href: str = a_tags_filtered[0].attrs['href']
            # Create a complete url for the medicine SmPC
            absolute_href = f'{base_link}{href}'
            # Append to medicine list
            medicine_urls.append(absolute_href)


def main():
    # EMC base page url
    medicines_base_url: str = 'https://www.medicines.org.uk'
    # EMC base search url
    emc_base_search_url: str = f'{medicines_base_url}/emc/search'
    # Define the partial ATC Code for searching medicines (in this case for HIV)
    # Todo: Could be generalized to receive this ATC Code from script argument.
    partial_atc_code_query: str = 'q=J05AF'
    # Show only medicines with health professional information
    healthcare_information_filter_query = 'filters=attributes[spc]'
    # Concatenate all search criteria (excluding mutable offset)
    emc_search_url: str = f'{emc_base_search_url}?{partial_atc_code_query}&{healthcare_information_filter_query}'

    current_offset: int = 1  # Strangely offset starts in 1 (no offset)
    limit: int = 50
    while True:
        to_search_url = f'{emc_search_url}&offset={current_offset}&limit={limit}&fullText=true'
        # Request search for atc code
        response: Response = requests.get(to_search_url)
        # Parse response
        soup = BeautifulSoup(response.content, features='html.parser')
        # Find search results elements
        search_results_elem = soup.find(
            name='div',
            attrs={
                'class': 'search-results'
            },
        )
        if search_results_elem is None:
            break
        # Filter non Tag elements (e.g. Navigable Strings)
        results_raw = [result for result in search_results_elem.children if isinstance(result, Tag)]
        if len(results_raw) == 0:
            break
        # Iterate over the result elements
        iterate_search_results(results_raw, medicines_base_url)
        if len(results_raw) != limit:
            break
        current_offset += limit

    # write urls to file
    with open(default_export_file, 'w', encoding='utf-8') as file:
        for url in medicine_urls:
            file.write(f'{url}\n')


if __name__ == '__main__':
    main()
