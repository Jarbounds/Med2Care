import os
from configparser import ConfigParser
from selenium.common import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait


def get_disease_active_principles_dict(directory_path: str) -> dict:
    disease_active_principles: dict = {}
    for disease_filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, disease_filename)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, 'r', encoding='utf-8') as file:
            disease_active_principles[disease_filename] = [
                active_principle.strip().lower() for active_principle in file.readlines()
            ]
    return disease_active_principles


def get_driver_instance(executable_path: str, headless: bool) -> Chrome:
    options: Options = Options()
    options.headless = headless
    options.add_argument("--window-size=1920,1080")

    service: Service = Service(executable_path)

    driver: Chrome = Chrome(options=options, service=service)
    return driver


def retrieve_matches(driver: Chrome, search_url: str, active_principles: list[str], exact_match: bool) -> list[str]:
    atc_codes: set = set()
    for active_principle in active_principles:
        driver.get(search_url)
        try:
            # Waiting page to load
            search_box_elem: WebElement = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.NAME, 'name'))
            # Insert active principle to search
            search_box_elem.send_keys(active_principle)
            # Find search button
            submit_button_elem = driver.find_element(By.CSS_SELECTOR, '[type=submit]')
            # Make search
            submit_button_elem.click()
            # Find all h2 headers (one of them is the result header)
            headers = driver.find_elements(By.CSS_SELECTOR, 'h2')
            found = False
            for header in headers:
                # Check if it is the correct header
                if header.text.startswith('Found'):
                    found = True
                    break
            if not found:
                continue

            # Finds all the results in the table (active principles matches)
            results_elem = driver.find_elements(By.CSS_SELECTOR, 'table > tbody > tr')
            for result_elem in results_elem:
                element = result_elem.find_elements(By.CSS_SELECTOR, 'td')
                # Get hte atc code that corresponds to the active principle
                atc_code_elem, active_principle_elem = tuple(element)
                # Compares for an exact match
                if exact_match and active_principle.casefold() == active_principle_elem.text.casefold():
                    atc_codes.add(atc_code_elem.text)
                    print(f'[Exact Match] Found ATC Code -> {atc_code_elem.text} '
                          f'for active principle -> {active_principle}')
                # elif not exact_match and active_principle.casefold() in active_principle_elem.text.casefold():
                #     atc_codes.add(atc_code_elem.text)
                #     print(f'[Partial Match] Found ATC Code -> {atc_code_elem.text} '
                #           f'for active principle -> {active_principle}')
        except TimeoutException:
            print('[TimeoutException] could not get the page in time')
    return list(sorted(atc_codes))


def main() -> None:
    # Reads configurations
    config: ConfigParser = ConfigParser()
    config.read('../../configurations/configurations.ini')

    active_principles_dir: str = config['PATH']['active_principles_dir']
    atc_codes_dir: str = config['PATH']['atc_codes_dir']
    atc_search_url: str = config['URL']['atc_search_url']
    exact_match: bool = config['CMP']['exact_match'].lower() == 'true'

    driver_path: str = config['PATH']['driver']
    headless: bool = config['DRIVER']['headless'].lower() == 'true'

    disease_active_principles: dict = get_disease_active_principles_dict(active_principles_dir)

    driver: Chrome = get_driver_instance(driver_path, headless)

    for disease in disease_active_principles.keys():
        active_principles: list[str] = disease_active_principles[disease]
        atc_codes = retrieve_matches(driver, atc_search_url, active_principles, exact_match)
        atc_codes_str = ''
        for atc_code in atc_codes:
            atc_codes_str += f'{atc_code}\n'
        atc_codes_str = atc_codes_str.rstrip('\n')
        with open(os.path.join(atc_codes_dir, disease), 'w', encoding='utf-8') as file:
            file.write(atc_codes_str)


if __name__ == '__main__':
    main()
