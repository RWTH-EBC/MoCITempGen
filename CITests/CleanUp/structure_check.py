import os
from pathlib import Path
from CI_Configuration.configuration import Config

class Structure_check(Config):
    def __init__(self):
        super().__init__()

    def check_ci_folder(self):
        dir_list = Config().return_file_dir()
        for dir in dir_list:
            dir_check = Path(dir)
            if dir_check.is_dir():
                print(f'Folder: {dir_check} exist.')
            else:
                print(f'Folder: {dir_check} does not exist and will be new created.')
                os.makedirs(dir)

    def check_ci_files(self):
        file_list = Config().return_file_list()
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