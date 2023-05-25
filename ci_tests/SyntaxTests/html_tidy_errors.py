import argparse
import os
import shutil
from tidylib import tidy_document
from ci_test_config import ci_config
import sys
from ci_tests.structure.config_structure import data_structure
from ci_tests.api_script.api_github import GitRepository
from ci_tests.structure.sort_mo_model import modelica_model
from pathlib import Path

# ! /usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""View errors in the HTML code of a Modelica .mo file

The script will
* collect all the HTML code (<html>...</html>) in the Modelica file and
* print out the original code with line numbers as well as
* the tidy version of the code (with line numbers).
* tidy-lib will look for errors and present the respective line numbers.

You can then inspect the code and make corrections to your Modelica
file by hand. You might want to use the tidy version as produced by
tidylib.

Example
-------
You can use this script on the command line and point it
to your Modelica file::

$ python html_tidy_errors.py <file> [file [...]]

Note:
-----
* This script uses Python 3.6 for printing syntax and
function parameter annotations.
* The script assumes that you have installed pytidylib

`$ pip install pytidylib`

* You also need to install the necessary dll's and
your python interpreter must be able to find the files.
In case of trouble just put the dll in your working dir.

[https://binaries.html-tidy.org/](https://binaries.html-tidy.org/)
"""


class HTML_Tidy(ci_config):
    """Class to Check Packages and run CheckModel Tests"""

    def __init__(self, package: str,
                 correct_overwrite: bool,
                 correct_backup: bool,
                 log: bool,
                 correct_view: bool,
                 library: str,
                 wh_library: str,
                 filter_whitelist: bool):
        """
        Args:
            package (): package to test
            correct_overwrite (): argument (default:false) overwrite models that failed html test
            correct_backup ():  argument(default:false) write a backup of a library
            log (): argument(default:false): write a html log of the html check
            correct_view (): argument(default:false): print models that failed html test
            library ():  library to test
            wh_library ():  library on the whitelist
            filter_whitelist (): argument(default:false): filter models that are on the whitelist
        """
        self.package = package
        self.correct_overwrite = correct_overwrite
        self.correct_backup = correct_backup
        self.log = log
        self.correct_view = correct_view
        self.library = library
        self.wh_library = wh_library
        self.filter_whitelist = filter_whitelist
        self.root_dir = self.package.replace(".", os.sep)
        data_structure().check_arguments_settings(self.root_dir)
        self.html_error_log = Path(self.root_dir, "HTML_error_log.txt")
        self.html_correct_log = Path(self.root_dir, "HTML_correct_log.txt")
        data_structure().check_file_setting(self.html_error_log, self.html_correct_log, create_flag=True)

        super().__init__()

    def _get_html_model(self):
        """
        Returns: return models to check
        """
        library_list = self._get_library_model()
        if self.filter_whitelist is True:
            wh_library_list = self._get_wh_library_model()
        else:
            wh_library_list = []
        html_model_list = self._remove_whitelist_model(library_list=library_list, wh_library_list=wh_library_list)
        return html_model_list

    def run_files(self):
        """
        Make sure that the parameter rootDir points to a Modelica package.
        Write errors to error message.
        """
        file_counter = 0
        html_model_list = self._get_html_model()
        for model in html_model_list:
            model_file = f'{model[:model.rfind(".mo")].replace(".", os.sep)}.mo'
            correct_code, error_list, html_correct_code, html_code = self._getInfoRevisionsHTML(model_file=model_file)
            if self.correct_backup:
                self._call_backup_old_files(model_file=model_file,
                                            document_corr=correct_code,
                                            file_counter=file_counter)
            if len(error_list) > 0 and error_list is not None:
                if self.correct_overwrite:
                    print(f'Error in file {model_file} with error:')
                    for error in error_list:
                        print(f'\n{error}\n')
                    print(f'Overwrite model: {model_file}\n')
                    self._call_correct_overwrite(model_name=model_file, document_corr=correct_code)
                    if self.log:
                            correct_code, error_list, html_correct_code, html_code = self._getInfoRevisionsHTML(
                                model_file=model_file)
                            self._call_write_log(model_file=model_file,
                                                 error_list=error_list,
                                                 html_correct_code=html_correct_code,
                                                 html_code=html_code)
                if self.correct_view:
                    self._call_correct_view(model_file=model_file,
                                            error_list=error_list,
                                            html_correct_code=html_correct_code,
                                            html_code=html_code)
                    if self.log:
                        self._call_write_log(model_file=model_file,
                                             error_list=error_list,
                                             html_correct_code=html_correct_code,
                                             html_code=html_code)


    def check_html_files(self, model_list: list = None):
        file_counter = 0
        if model_list is not None and len(model_list) > 0:
            for model in model_list:
                model_file = Path(model.replace(".", os.sep) + ".mo")  # todo: das kann weg, wenn ich sort angepasst haben
                correct_code, error_list, html_correct_code, html_code = self._getInfoRevisionsHTML(
                    model_file=model_file)
                if self.correct_backup:
                    self._call_backup_old_files(model_file=model_file,
                                                document_corr=correct_code,
                                                file_counter=file_counter)
                if len(error_list) > 0:
                    if self.correct_overwrite:
                        print(f'Error in file {model_file} with error:')
                        for error in error_list:
                            print(f'\n{error}\n')
                        print(f'Overwrite model: {model_file}\n')
                        self._call_correct_overwrite(model_name=model_file, document_corr=correct_code)
                        if self.log:
                            correct_code, error_list, html_correct_code, html_code = self._getInfoRevisionsHTML(
                                model_file=model_file)
                            self._call_write_log(model_file=model_file,
                                                 error_list=error_list,
                                                 html_correct_code=html_correct_code,
                                                 html_code=html_code)
                    if self.correct_view:
                        self._call_correct_view(model_file=model_file,
                                                error_list=error_list,
                                                html_correct_code=html_correct_code,
                                                html_code=html_code)
                        if self.log:
                            self._call_write_log(model_file=model_file,
                                                 error_list=error_list,
                                                 html_correct_code=html_correct_code,
                                                 html_code=html_code)



    def call_read_log(self):
        """
        Read the html log.
        Returns: variable with 0 or 1
        """
        err_list = self.read_log_file()
        var = self._write_exit(err_list=err_list)
        data_structure().create_path(self.result_dir, self.result_syntax_dir)
        data_structure().prepare_data(del_flag=True,
                                      source_target_dict={self.html_error_log: self.result_syntax_dir,
                                                          self.html_correct_log: self.result_syntax_dir})
        return var

    def _call_write_log(self, model_file, error_list, html_correct_code, html_code):
        """
        Write a log file of the html test.
        Args:
            model_file (): model to check
            error_list (): list of errors for each model
            html_correct_code (): corrected html code
            html_code (): html code of a modelica file
        """

        if len(error_list) > 0 and error_list is not None:
            with open(f'{self.html_error_log}', "a", encoding="utf-8") as error_log_file,  open(f'{self.html_correct_log}', "a", encoding="utf-8") as correct_log_file:
                print(f'Error-log-file is saved in {self.html_error_log}')
                print(f'Correct-log-file is saved in {self.html_correct_log}')
                error_log_file.write(f'\n---- {model_file} ----')
                correct_log_file.write(
                    f'\n---- {model_file} ----\n-------- HTML Code --------\n{html_code}\n-------- Corrected Code --------\n{html_correct_code}\n-------- Errors --------')
                for error in error_list:
                    error_log_file.write(f'\n{error}\n')
                    correct_log_file.write(f'\n{error}\n')

    @staticmethod
    def _call_correct_view(model_file, error_list, html_correct_code, html_code):
        """
        print the corrected html code
        Args:
            model_file (): model to test
            error_list (): list of errors for each model
            html_correct_code (): corrected html code
            html_code (): html code of a modelica file
        """
        if len(error_list) > 0:
            print(
                f'\n---- {model_file} ----\n-------- HTML Code --------\n{html_code}\n-------- Corrected Code --------\n{html_correct_code}\n-------- Errors --------')
            for error in error_list:
                print(f'\n{error}\n')

    def join_body(self, html_list: list) -> str:
        """
        Joins a list of strings into a single string and makes replacements
        Args:
            html_list ():
            The html code is escaped in Modelica. To feed it to tidy-lib
            we need to remove the escape characters.
        Returns: body
        """
        body = ''.join(html_list)
        body = self._make_string_replacements(the_string=body, substitutions_dict={'\\"': '"'})
        return body

    @staticmethod
    def _make_string_replacements(the_string: str, substitutions_dict: dict = {'\\"': '"'}) -> str:
        """
        Takes a string and replaces according to a given dictionary
		Parameters
		----------
		the_string : str
				The string that contains replaceable text.
		substitutions_dict : dict
				A dictionary with key:value pairs for old and new text.
		Returns
		-------
		str
				The modified string.
        Args:
            theString ():
            substitutions_dict ():

        Returns:
        """
        for k, v in substitutions_dict.items():
            the_string = the_string.replace(k, v)
        return the_string

    def _getInfoRevisionsHTML(self, model_file):
        """
        Returns a list that contains the html code
		This function returns a list that contain the html code of the
		info and revision sections. Each element of the list
		is a string.
		Parameters
		----------
		model_file : str - The name of a Modelica source file.
		Returns
		-------
		The list of strings of the info and revisions section.
        Args:
            model_file ():
        Returns:
        """
        with open(model_file, mode="r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        nLin = len(lines)
        is_tag_closed = True
        html_section_code = list()
        error_list = list()
        html_correct_code = list()
        html_code = list()
        all_code = ""
        for i in range(nLin):
            all_code = f'{all_code}{lines[i]}'
            if is_tag_closed:  # search for opening tag
                idxO = lines[i].find("<html>")
                if idxO > -1:  # search for closing tag on same line as opening tag
                    idxC = lines[i].find("</html>")
                    if idxC > -1:
                        html_section_code.append(f'{lines[i][idxO + 6:idxC]}')
                        is_tag_closed = True
                    else:
                        html_section_code.append(f'{lines[i][idxO + 6:]}')
                        is_tag_closed = False
            else:  # search for closing tag
                idxC = lines[i].find("</html>")
                if idxC == -1:  # closing tag not found, copy full line
                    html_section_code.append(lines[i])
                else:  # search for opening tag on same line as closing tag
                    html_section_code.append(f'{lines[i][0:idxC]}')
                    html_string = ''.join(html_section_code)
                    html_code.append(html_string)

                    html_corr, errors = self._htmlCorrection(html_section_code)

                    html_correct_code.append(html_corr)
                    if len(errors) > 0:
                        error_list.append(errors)
                    all_code = all_code.replace(html_string, html_corr)

                    html_section_code = list()
                    is_tag_closed = True
                    idxO = lines[i].find("<html>")
                    if idxO > -1:
                        html_section_code.append(f'{lines[i][idxO + 6:]}')
                        is_tag_closed = False
        html_code = ''.join(html_code)
        html_correct_code = ''.join(html_correct_code)
        '''
        code = ""
        for line in all_code.splitlines():
            #line = self.correct_p_align(line=line)
            #line = self.correct_table_summary(line=line)
            #line = self.correct_font(line=line)
            #line = self.correct_th_align(line=line)
            #line = self.correct_img_atr(line=line)
            #line = self.delete_html_revision(line=line)
            code += line + '\n'
        '''
        return all_code, error_list, html_correct_code, html_code

    @staticmethod
    def delete_html_revision(line, ):
        """
        Delete revision
        Args:
            line ():
        Returns:
        """
        htmlTag = line.encode("utf-8").find(b"</html>")
        htmlCloseTag = line.encode("utf-8").find(b"<html>")
        RevTag = line.encode("utf-8").find(b"revision")
        if htmlTag > -1 and RevTag > -1:
            if htmlCloseTag > -1:
                line = ""
        return line

    @staticmethod
    def correct_img_atr(line):
        """
        Correct img and check for missing alt attributed
        Args:
            line ():
        Returns:
        """
        imgTag = line.encode("utf-8").find(b"img")
        if imgTag > -1:
            imgCloseTagIndex = line.find(">", imgTag)
            imgAltIndex = line.find("alt", imgTag)
            if imgCloseTagIndex > -1 and imgAltIndex == -1:  # if close tag exists but no alt attribute, insert alt attribute and change > to />
                line = line[:imgTag] + line[imgTag:].replace(">", ' alt="" />', 1)
            elif imgCloseTagIndex > -1 and imgAltIndex > -1:  # if close tag exists and alt attribute exists, only change > to />
                line = line[:imgTag] + line[imgTag:].replace(">", ' />', 1)

            elif imgCloseTagIndex == -1:  # if close tag is not in the same line
                line = line
        else:  # if no close tag was found in previous line, but opening tag found search for close on this line with same
            imgCloseTagIndex = line.find(">")
            imgAltIndex = line.find("alt")
            if imgCloseTagIndex > -1 and imgAltIndex == -1:
                line = line[:imgCloseTagIndex] + \
                       line[imgCloseTagIndex:].replace(">", ' alt="" />', 1)
            elif imgCloseTagIndex > -1 and imgAltIndex > -1:
                line = line[:imgCloseTagIndex] + \
                       line[imgCloseTagIndex:].replace(">", ' />', 1)
            elif imgCloseTagIndex == -1:
                line = line
        return line

    @staticmethod
    def correct_th_align(line):
        """
        Correct algin with th and replace style="text-align"
        Args:
            line ():
        Returns:
        """

        alignTag = line.encode("utf-8").find(b"align")
        thTag = line.encode("utf-8").find(b"th")
        if alignTag > -1 and thTag > -1:
            line = (line.replace('\\', ''))
        return line

    @staticmethod
    def _call_correct_overwrite(model_name, document_corr):
        """
        This function overwrites the old modelica files with the corrected files
        Args:
            model_name ():
            document_corr ():
        """
        os.remove(model_name)
        newfile = open(model_name, "w+b")
        newfile.write(document_corr.encode("utf-8"))

    def _call_backup_old_files(self, model_file, document_corr, file_counter):
        """
        This function backups the root folder and creates the corrected files
        Args:
            model_file:
            document_corr:
            file_counter:
        """
        root_dir = self.package.replace(".", os.sep)
        if os.path.exists(root_dir + "_backup") is False and file_counter == 1:
            shutil.copytree(root_dir, root_dir + "_backup")
            print(f'You can find your backup under {root_dir}_backup')
        os.remove(model_file)
        newfile = open(model_file, "w+b")
        newfile.write(document_corr.encode("utf-8"))

    @staticmethod
    def correct_font(line):
        """
        Replace font to style für html5
        Args:
            line ():

        Returns:
        """
        styleTag_1 = line.encode("utf-8").find(b"style=")
        styleTag_2 = line.encode("utf-8").find(b"color")
        fontTag = line.encode("utf-8").find(b"<font")
        rfontTag = line.encode("utf-8").rfind(b"</font>")
        if styleTag_1 > -1 and styleTag_2 > -1:
            if fontTag > -1 and rfontTag > -1:
                sline = (line[fontTag:rfontTag].replace('\\', ''))
                sline = sline.replace('"', '')
                sline = sline.replace('<font', '<span')
                sline = (sline.replace('color:', '"color:'))
                sline = sline.replace(';>', '">')
                line = line[:fontTag] + sline + line[rfontTag:].replace('</font>', '</span>')
        elif fontTag > -1 and rfontTag > -1:
            sline = (line[fontTag:rfontTag].replace('\\', ''))
            sline = sline.replace('"', '')
            sline = sline.replace('<font', '<span')
            sline = (sline.replace('color=', 'style="color:'))
            sline = (sline.replace('>', '">'))
            line = line[:fontTag] + sline + line[rfontTag:].replace('</font>', '</span>')
        return line

    @staticmethod
    def correct_table_summary(line):
        """
        delete Summary in table and add <caption> Text </caption>
        Args:
            line ():
        Returns:
        """
        tableTag = line.encode("utf-8").find(b"<table")
        sumTag = line.encode("utf-8").find(b"summary")
        if tableTag > -1 and sumTag > -1:
            line = line[:sumTag] + "> " + line[sumTag:].replace('summary=', '<caption>', 1)
            line = (line.replace('">', '</caption>', 1))
        return line

    @staticmethod
    def correct_p_align(line):
        """
        Correct align in p and replace style="text-align"
        Wrong: <p style="text-align:center;">
        # Correct: <p style="text-align:center;">
        # Correct: <p style="text-align:center;font-style:italic;color:blue;">k = c<sub>p</sub>/c<sub>v</sub> </p>
        # Correct: <p style="text-align:center;font-style:italic;">
        Args:
            line ():

        Returns:
        """
        pTag = line.encode("utf-8").find(b"<p")
        alignTag = line.encode("utf-8").find(b"align")
        closetag = line.encode("utf-8").find(b">")
        styleTag = line.encode("utf-8").find(b"text-align:")
        if styleTag > -1:
            return line
        elif pTag > -1 and alignTag > -1:
            sline = (line[alignTag:closetag + 1].replace('\\', ''))
            sline = (sline.replace('align="', 'style=text-align:'))
            sline = (sline.replace('style=', 'style="'))
            sline = (sline.replace(';', ''))
            CloseTag_2 = sline.encode("utf-8").rfind(b">")
            if CloseTag_2 > -1:
                sline = (sline.replace('">', ';">'))
            sline = sline.replace('""', '"')
            line = (line[:alignTag] + sline + line[closetag + 1:])
            StyleCount = line.count("style=")
            if StyleCount > 1:
                line = line.replace('style="', '')
                line = line.replace('"', '')
                line = line.replace(';>', ';">')
                pTag = line.encode("utf-8").find(b"<p")
                tline = line[pTag + 2:]
                tline = ('style="' + tline.lstrip())
                tline = tline.replace(" ", ";")
                closetag = line.encode("utf-8").find(b">")
                line = (line[:pTag + 3] + tline + line[closetag + 1:])
        return line

    def read_log_file(self):
        """
        read logfile for possible errors
        Returns: return a list of error
        """
        with open(self.html_error_log, "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()

        err_list = []
        warning_table = f'Warning: The summary attribute on the <table> element is obsolete in HTML5'
        warning_font = f'Warning: <font> element removed from HTML5'
        warning_align = f'Warning: <p> attribute "align" not allowed for HTML5'
        warning_img = f'Warning: <img> lacks "alt" attribute'
        warning_th_align = f' Warning: <th> attribute "align" not allowed for HTML5'
        except_warning_list = [warning_img, warning_align, warning_table, warning_th_align]
        warning_list = [warning_font]

        for line in lines:
            line = line.replace("\n", "")
            for warning in warning_list:
                if line.find(warning) > -1:
                    err_list.append(line)
                    continue
            if line.find("--") > -1 and line.find(".mo") > -1:
                continue
            elif line.find("Warning") > -1:
                err_list.append(line)
                for warning in except_warning_list:
                    if line.find(warning) > -1:
                        err_list.remove(line)
                        continue
        return err_list

    def _write_exit(self, err_list):
        """
        If an entry in the error list exist, the check failed
        Args:
            err_list (): list with error of html check
        Returns: return a variable (if 0: check was successful, 1: check failed)
        """
        try:
            exit_file = open(self.config_ci_exit_file, "w")
            if len(err_list) > 0:
                print(f'{self.CRED}Syntax Error:{self.CEND} Check HTML-logfile')
                exit_file.write("exit 1")
                var = 1
            else:
                print(f'{self.green}HTML Check was successful!{self.CEND}')
                exit_file.write("exit 0")
                var = 0
            exit_file.close()
            return var
        except IOError:
            print(f'Error: File {self.config_ci_exit_file} does not exist.')

    def _htmlCorrection(self, html_code):
        """
        Args:
            html_code (): html code of a modelica file
        Returns:
            document_corr (): return corrected code
            errors (): return the error of the html code
        """
        substitutions_dict: dict = {'"': '\\"', '<br>': '<br/>', '<br/>': '<br/>'}
        html_str = self.join_body(html_list=html_code)

        html_correct, errors = tidy_document(f"{html_str}",
                                             options={'doctype': 'html5',
                                                      'show-body-only': 1,
                                                      'numeric-entities': 1,
                                                      'output-html': 1,
                                                      'wrap': 72,
                                                      'show-warnings': 1,
                                                      'alt-text': 1,
                                                      'indent': 1
                                                      })
        document_corr = self._make_string_replacements(the_string=html_correct,
                                                       substitutions_dict=substitutions_dict)
        return document_corr, errors

    def _get_wh_library_model(self):
        """
        Returns: models from html whitelist, if whitelist not found return an empty list
        """
        wh_library_list = []
        try:
            file = open(self.wh_html_file, "r")
            lines = file.readlines()
            file.close()
            for line in lines:
                if line.find(".mo") > -1:
                    line = line.replace(self.wh_library, self.library)
                    line = line.replace("\n", "")
                    wh_library_list.append(line)
            return wh_library_list
        except IOError:
            print(f'Error: File {self.wh_html_file} does not exist. Check without a whitelist.')
            return wh_library_list

    def _get_library_model(self):
        """
        Returns: library models to check
        """
        library_list = []
        for subdir, dirs, files in os.walk(self.package.replace(".", os.sep)):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo"):
                    model = filepath.replace(os.sep, ".")
                    model = model[model.rfind(self.library):]
                    library_list.append(model)
        return library_list

    @staticmethod
    def _remove_whitelist_model(library_list, wh_library_list):
        """
        remove models that are on the whitelist
        Returns: return a list of models, that are not on the whitelist
        """
        remove_models_list = []
        for model in library_list:
            for wh_model in wh_library_list:
                if model == wh_model:
                    remove_models_list.append(model)
        for remove_model in remove_models_list:
            library_list.remove(remove_model)
        return library_list


class htmlWhitelist(ci_config):

    def __init__(self):
        """
        Args:
        """
        super().__init__()

    def write_whitelist(self, model_list):
        """
        write a whitelist with models
        Args:
            model_list (): models on the whitelist
        """
        file = open(self.wh_html_file, "w")
        for model in model_list:
            file.write("\n" + model + ".mo" + "\n")
        file.close()


class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(
            description='Run HTML correction on files')
        # [Library - settings]
        parser.add_argument("--packages", metavar="AixLib.Package",
                            help="Package to test for a html test")
        parser.add_argument("--library", default="AixLib", help="Library to test")
        parser.add_argument("--wh-library", default="IBPSA", help="Library that is written to a whitelist")
        parser.add_argument("--git-url", default="https://github.com/ibpsa/modelica-ibpsa.git",
                            help="url repository of library for whitelist")
        parser.add_argument("--repo-dir", default="modelica-ibpsa",
                            help="url repository of library for whitelist")
        parser.add_argument("--root-wh-library",
                            help="library on a whitelist")
        # [ bool - flag]
        parser.add_argument("--correct-overwrite-flag", action="store_true", default=False,
                            help="correct html code in modelica files and overwrite old files")
        parser.add_argument("--correct-backup-flag", action="store_true", default=False,
                            help="backup old files")
        parser.add_argument("--log-flag", action="store_true",
                            default=True, help="create logfile of model with errors")
        parser.add_argument("--whitelist-flag", action="store_true", default=False,
                            help="Create a new whitelist for a Library")
        parser.add_argument("--correct-view-flag", action="store_true", default=False,
                            help="Check and print the Correct HTML Code")
        parser.add_argument("--filter-whitelist-flag", default=False, action="store_true", help="Argument for ")
        args = parser.parse_args()
        return args


if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    conf = ci_config()
    check = data_structure()
    check.create_path(conf.config_ci_dir)
    check.create_files(conf.config_ci_exit_file)
    mo = modelica_model()
    if args.whitelist_flag is True:
        check.create_path(conf.wh_ci_dir)
        check.create_files(conf.wh_html_file)
        GitRepository.clone_repository(repo_dir=args.root_wh_library, git_url=args.git_url)
        model_list = mo.get_models(library=args.wh_library,
                                   path=args.root_wh_library,
                                   simulate_flag=False,
                                   extended_ex_flag=False)
        htmlWhitelist().write_whitelist(model_list=model_list)
        data_structure.prepare_data(source_target_dict={conf.wh_html_file: conf.result_whitelist_dir})
        exit(0)
    else:
        html_tidy_check = HTML_Tidy(package=args.packages,
                                    correct_overwrite=args.correct_overwrite_flag,
                                    correct_backup=args.correct_backup_flag,
                                    log=args.log_flag,
                                    correct_view=args.correct_view_flag,
                                    library=args.library,
                                    wh_library=args.wh_library,
                                    filter_whitelist=args.filter_whitelist_flag)

        html_model = mo.get_option_model(library=args.library,
                                         package=args.library,
                                         filter_wh_flag=args.filter_whitelist_flag,
                                         wh_library=args.wh_library,
                                         root_package=Path(args.library))
        html_tidy_check.run_files()
        html_tidy_check.check_html_files(model_list=html_model)
        if args.log_flag is True:
            variable = html_tidy_check.call_read_log()
            exit(variable)
        if args.correct_overwrite_flag is False and args.correct_backup_flag is False and args.log_flag is False and args.correct_view_flag is False:
            print("please use -h or --help for help")
