import os
from configparser import ConfigParser
from utils.utils import transfer_file


def main():
    config: ConfigParser = ConfigParser()
    config.read('../configurations/config.ini')

    transfer_option: str = config['TRANSFER']['next_stage_option']
    src_path: str = config['PATH']['staged_data_dir']
    dst_path: str = config['PATH']['next_stage_data_dir']

    file_list: list = os.listdir(src_path)

    transfer_file(
        lst_files=file_list,
        src=src_path,
        dst=dst_path,
        flag=transfer_option
    )


if __name__ == '__main__':
    main()
