from setuptools import setup, find_packages
import glob
import os

with open(f'ci_tests{os.sep}README.md', 'r') as f:
    long_description = f.read()
with open(f"ci_tests{os.sep}requirements.txt", 'r') as f:
    required = f.read().splitlines()
VERSION = "0.1.0"


setup(
    name='Dymola_Python_test',
    version='0.1.0',
    description='Check dymola files with python-dymola-interface',
    license="???",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Sven Hinrichs',
    author_email='sven.hinrichs@eonerc.rwth-aachen.de',
    url="https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests",
    packages=find_packages(include=['ci_tests*']),
    include_package_data=True,
    python_requires='>=3.9.0',
    install_requires=[required
    ],
)
