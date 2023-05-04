import os
from pathlib import Path
import argparse
from ci_test_config import ci_config
import sys

class Structure_check(ci_config):
    def __init__(self):
        super().__init__()

    def check_ci_folder(self):
        dir_list = self.return_file_dir()
        for directionary in dir_list:
            dir_check = Path(directionary)
            if dir_check.is_dir():
                print(f'Folder: {dir_check} exist.')
            else:
                print(f'Folder: {dir_check} does not exist and will be new created.')
                os.makedirs(directionary)

    def check_ci_files(self):
        file_list = self.return_file_list()
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

class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description="Config files for the CI")  # Configure the argument parser
        check_test_group = parser.add_argument_group("Arguments to build the CI structure")
        check_test_group.add_argument("--config-dir", default=False, action="store_true")
        check_test_group.add_argument("--create-path", default=False, action="store_true")
        args = parser.parse_args()  # Parse the arguments
        return args

if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    check = Structure_check()
    if args.create_path is True:
        if args.config_dir is True:
            conf._create_folder(path=conf.config_dir)
    check.check_ci_folder()
    check.check_ci_files()
