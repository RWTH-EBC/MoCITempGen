import os
import toml
from pathlib import Path


def check_ci_folder(dir_list):
    for dir in dir_list:
        new_dir = dir.split("=")[1].strip().replace('{os.sep}', os.sep)
        dir_check = Path(new_dir)
        if dir_check.is_dir():
            print(f'Folder: {dir_check} exist.')
        else:
            print(f'Folder: {dir_check} does not exist and will be new created.')
            os.makedirs(new_dir)


def check_ci_files(file_list):
    for file in file_list:
        new_file = file.split("=")[1].strip().replace('{os.sep}', os.sep)
        file_check = Path(new_file)
        if file_check.is_file():
            print(f'File: {new_file} exist.')
        else:
            print(f'File: {new_file} does not exist and will be new created.')
            file_check.touch(exist_ok=True)


if __name__ == '__main__':
    setting_file = f'CITests{os.sep}_config_CI_tests.toml'
    data = toml.load(setting_file)
    files = data["files"]
    file_list = [files["wh_file"], files["ref_whitelist_file"], files["html_wh_file"], files["show_ref_file"], files["update_ref_file"],
                 files["chart_temp_file"], files["index_temp_file"], files["layout_temp_file"], files["exit_file"], files["ref_file"],
                 files["ch_file"], files["new_ref_file"]]
    folder = data["folder"]
    dir_list = [folder["artifacts_dir"], folder["chart_dir"], folder["ref_file_dir"], folder["resource_dir"]]
    check_ci_files(file_list)
    check_ci_folder(dir_list)
