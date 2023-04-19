from utils.myconfiguration import MyConfiguration as Config
from utils.utils import transfer_file


def main():
    config: Config = Config.get_instance()

    transfer_option: str = config.transfer_option
    path_dataset: str = config.path_ds
    dataset_filename: str = config.ds_name
    dst_dataset_path: str = config.path_algorithms

    transfer_file(
        lst_files=[dataset_filename],
        src=path_dataset,
        dst=dst_dataset_path,
        flag=transfer_option
    )


if __name__ == '__main__':
    main()
