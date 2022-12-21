import os
import shutil
from Dymola_python_tests.CI_test_config import CI_config


class Prepare_result_class(CI_config):
    def __init__(self):
        super().__init__()


    def remove_files(self, file):
        os.remove(file)
        print(f'Remove file: {file}')

    def prepare_data_path(self, path):
        try:
            if not os.path.exists(path):
                print(f'Create path: {path}')
                os.makedirs(path)
            else:
                print(f'Path "{path}" exist.')
        except FileExistsError:
            print(f'Find no folder')
            pass

    def prepare_data_files(self, file_path_dict):
        for file in file_path_dict:
            print(file)
            #shutil.copy(path, file)
            #print(f'Result file {file} was moved to {path}')




if __name__ == '__main__':

    pass