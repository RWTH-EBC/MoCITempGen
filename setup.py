from setuptools import setup, find_packages
import os
from pathlib import Path

with open("Dymola_python_tests/README.md", 'r') as f:
    long_description = f.read()
with open("Dymola_python_tests/ci_tests/requirements.txt", 'r') as f:
    required = f.read().splitlines()
with open("Dymola_python_tests/ci_tests/dependency_requirements.txt", 'r') as f:
    dep_required = f.read().splitlines()
version = "0.1.0"

def copy_non_code_file(non_code_dir:list, not_include:list):
    path_file_dict = {}
    for filename in non_code_dir:
        _dir = filename.replace(".", os.sep)
        for subdir, dirs, files in os.walk(_dir):
            file_list = []
            for file in files:
                filepath = Path(subdir, file)
                file_name = Path(filepath.name)
                file_list.append(str(file_name))
                for end in not_include:
                    if file_name.suffix == end:
                        file_list.remove(str(file_name))
            if len(file_list) > 0:
                path_file_dict[str(filepath.parent).replace(os.sep, ".")] = file_list
            continue
    return path_file_dict


setup(
    name='Dymola_Python_test',
    version=version,
    description='Check dymola files with python-dymola-interface',
    license="LICENSE",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Sven Hinrichs',
    author_email='sven.hinrichs@eonerc.rwth-aachen.de',
    url="https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests",
    packages=find_packages(include=['ci_tests*',
                                    'config*',
                                    'templates*']),
    include_package_data=True,
    package_data=copy_non_code_file(non_code_dir=f'ci_tests',
                                    not_include=[".py", ".Dockerfile", ".pyc"]),
    python_requires='>=3.9.0',
    install_requires=[required],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    dependency_links=dep_required
)
