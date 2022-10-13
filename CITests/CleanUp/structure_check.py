import os
import sys
from pathlib import Path

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


if __name__ == '__main__':
    check = Structure_check()
    check.check_ci_folder()
    check.check_ci_files()
