import json
import os

def _read_file():
    f = open(f'Dymola_python_tests{os.sep}CI_test_config.json')
    data = json.load(f)
    print(data["whitelist"])

if __name__ == '__main__':
    _read_file()


