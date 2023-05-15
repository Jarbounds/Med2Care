from ELT.src.emc import get_medicines_url, extract_medicine_data_from_url, get_atc_codes
import cleaning_data
import remove_duplicate_files
import sys


def main(atc_step=False, url_step=False, extract_step=False, clean_step=False, duplicate_step=False):

    if atc_step:
        get_atc_codes.main()
    if url_step:
        get_medicines_url.main()
    if extract_step:
        extract_medicine_data_from_url.main()
    if clean_step:
        cleaning_data.main()
    if duplicate_step:
        remove_duplicate_files.main()


if __name__ == '__main__':
    is_atc_step = False
    is_url_step = False
    is_extract_step = False
    is_clean_step = False
    is_duplicate_step = False

    for arg in sys.argv:
        if arg in ['-atc', '--ATC']:
            is_atc_step = True
        elif arg in ['-url', '--URL']:
            is_url_step = True
        elif arg in ['-ex', '--Extract']:
            is_extract_step = True
        elif arg in ['-clean', '--Clean']:
            is_clean_step = True
        elif arg in ['-dup', '--Duplicate']:
            is_duplicate_step = True
    main(
        atc_step=is_atc_step,
        url_step=is_url_step,
        extract_step=is_extract_step,
        clean_step=is_clean_step,
        duplicate_step=is_duplicate_step,
    )
