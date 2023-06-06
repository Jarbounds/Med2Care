from ELT.src.medlineplus import get_medicines_url, extract_medicine_data_from_url
import cleaning_data
import remove_duplicate_files
import sys


def main(url_step=False, extract_step=False, clean_step=False, duplicate_step=False):

    if url_step:
        get_medicines_url.main()
    if extract_step:
        extract_medicine_data_from_url.main()
    if clean_step:
        cleaning_data.main()
    if duplicate_step:
        remove_duplicate_files.main()


if __name__ == '__main__':
    is_url_step = False
    is_extract_step = False
    is_clean_step = False
    is_duplicate_step = False

    for arg in sys.argv:
        if arg in ['-url', '--URL']:
            is_url_step = True
        elif arg in ['-ex', '--Extract']:
            is_extract_step = True
        elif arg in ['-clean', '--Clean']:
            is_clean_step = True
        # elif arg in ['-dup', '--Duplicate']:
        #     is_duplicate_step = True
    main(
        url_step=is_url_step,
        extract_step=is_extract_step,
        clean_step=is_clean_step,
        duplicate_step=is_duplicate_step,
    )
