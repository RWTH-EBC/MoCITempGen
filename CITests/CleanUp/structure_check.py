import os
import sys
from pathlib import Path
import argparse
# TODO Get rid of all references to "Dymola_python_tests"
sys.path.append('Dymola_python_tests/CITests/CI_Configuration')
from configuration import CI_conf_class


class Structure_check(CI_conf_class):
    def __init__(self):
        super().__init__()

    def check_ci_folder(self):
        dir_list = CI_conf_class().return_file_dir()
        for directionary in dir_list:
            dir_check = Path(directionary)
            if dir_check.is_dir():
                print(f'Folder: {dir_check} exist.')
            else:
                print(f'Folder: {dir_check} does not exist and will be new created.')
                os.makedirs(directionary)

    def check_ci_files(self):
        file_list = CI_conf_class().return_file_list()
        for file in file_list:
            file_check = Path(file)
            if file_check.is_file():
                print(f'File: {file} exist.')
            else:
                print(f'File: {file} does not exist and will be new created.')
                file_check.touch(exist_ok=True)

    def _create_folder(self, path):
        try:
            if not os.path.exists(path):
                print(f'Create path: {path}')
                os.makedirs(path)
            else:
                print(f'Path "{path}" exist.')
        except FileExistsError:
            print(f'Find no folder')
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Config files for the CI")  # Configure the argument parser
    check_test_group = parser.add_argument_group("Arguments to build the CI structure")
    check_test_group.add_argument("--config-dir", default=False, action="store_true")
    check_test_group.add_argument("--create-path", default=False, action="store_true")
    args = parser.parse_args()  # Parse the arguments
    check = Structure_check()
    if args.create_path is True:
        if args.config_dir is True:
            conf._create_folder(path=conf.config_dir)
    check.check_ci_folder()
    check.check_ci_files()
