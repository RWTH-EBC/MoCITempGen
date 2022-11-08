import argparse
import os
import sys
from pathlib import Path

sys.path.append('Dymola_python_tests/CITests/CI_Configuration')
from configuration import CI_conf_class


class Lock_model(CI_conf_class):

    def __init__(self, library, wh_library):
        """
        Args:
            library ():
            wh_library ():
        """
        self.library = library
        self.wh_library = wh_library
        super().__init__()

    def sort_whitelist_model(self):
        """
        Read whitelist and return a list.
        Sort List of models.

        Returns:
            model_list ()
        """
        try:
            wh = open(self.wh_html_file, "r")
            whitelist_lines = wh.readlines()
            wh.close()
            model_list = []
            for line in whitelist_lines:
                if len(line) == 1 or line.find("package.mo") > -1 or line.find("package.order") > -1 or line.find(
                        "UsersGuide") > -1:
                    continue
                else:
                    line = line.replace(self.wh_library, self.library)
                    mo = line.replace(".", os.sep, line.count(".") - 1).lstrip()
                    mo = mo.strip()
                    model_list.append(mo)
            return model_list

        except IOError:
            print(f'Error: File {self.wh_html_file} does not exist.')
            exit(1)

    def call_lock_model(self):
        mo_li = self.sort_whitelist_model()
        for model in mo_li:
            if Path(model).is_file():
                result = self.get_last_line(model_file=model)
                if len(result[0]) == 0:
                    continue
                if result[1] is False:
                    new_content = self.lock_model(model, result[0])
                    self.write_lock_model(model, new_content)
                else:
                    print(f'Already locked: {model}')
                    continue
            else:
                print(f'\n{model} File does not exist.')
                continue

    @staticmethod
    def get_last_line(model_file):
        """
        Args:
            model_file ():
        Returns:
        """
        model_part = []
        flag = '__Dymola_LockedEditing="Model from IBPSA");'
        flag_tag = False
        try:
            if Path(model_file).is_file():
                infile = open(model_file, "r")
                for lines in infile:
                    model_part.append(lines)
                    if lines.find(flag) > -1:
                        flag_tag = True
                infile.close()
                return model_part, flag_tag
            else:
                print(f'\n{model_file}\nFile does not exist.')
        except IOError:
            print(f'Error: File {model_file} does not exist.')

    @staticmethod
    def lock_model(model, content):
        """

        Args:
            model ():
            content ():

        Returns:

        """
        mo = model[model.rfind(os.sep) + 1:model.rfind(".mo")]
        last_entry = content[len(content) - 1]
        flag = '   __Dymola_LockedEditing="Model from IBPSA");'
        old_html_flag = '</html>"));'
        new_html_flag = '</html>"),  \n' + flag
        old = ');'
        new = ', \n' + flag
        if last_entry.find(mo) > -1 and last_entry.find("end") > -1:
            flag_lines = content[len(content) - 2]
            if flag_lines.isspace():
                flag_lines = content[len(content) - 3]
                del content[len(content) - 2]
            if flag_lines.find(old_html_flag) > -1:
                flag_lines = flag_lines.replace(old_html_flag, new_html_flag)
            elif flag_lines.find(old) > -1:
                flag_lines = flag_lines.replace(old, new)
            del content[len(content) - 2]
            content.insert(len(content) - 1, flag_lines)
            return content
        else:
            flag_lines = content[len(content) - 1]
            if flag_lines.find(old_html_flag) > -1:
                flag_lines = flag_lines.replace(old_html_flag, new_html_flag)
            elif flag_lines.find(old) > -1:
                flag_lines = flag_lines.replace(old, new)
            del content[len(content) - 1]
            content.insert(len(content), flag_lines)
            return content

    @staticmethod
    def write_lock_model(model, new_content):
        """
        Args:
            model ():
            new_content ():
        """
        try:
            print("lock object: " + model)
            outfile = open(model, 'w')
            new_content = (' '.join(new_content))
            outfile.write(new_content)
            outfile.close()
        except IOError:
            print(f'Error: File {model} does not exist.')
            exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lock models.')
    unit_test_group = parser.add_argument_group("arguments to run class Lock_model")
    unit_test_group.add_argument("-L", "--library", default="AixLib", help="Library to test")
    unit_test_group.add_argument("-wh-l", "--wh-library", help="Library to test")
    args = parser.parse_args()
    lock = Lock_model(library=args.library, wh_library=args.wh_library)
    lock.call_lock_model()
