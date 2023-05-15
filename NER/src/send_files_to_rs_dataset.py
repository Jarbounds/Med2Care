import os
from configparser import ConfigParser
from utils.utils import transfer_file


def main():
    config: ConfigParser = ConfigParser()
    config.read('../configurations/configurations.ini')

    transfer_option: str = config['TRANSFER']['next_stage_option']
    src_path_entities: str = config['PATH']['path_to_entities_json']
    dst_path_entities: str = config['PATH']['path_next_stage_entities']

    file_list = os.listdir(src_path_entities)

    transfer_file(
        lst_files=file_list,
        src=src_path_entities,
        dst=dst_path_entities,
        flag=transfer_option
    )


if __name__ == '__main__':
    main()
