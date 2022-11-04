import argparse
import io
import os
import shutil
import sys
from git import Repo
from tidylib import tidy_document

sys.path.append('Dymola_python_tests/CITests/CI_Configuration')
from configuration import CI_conf_class

# ! /usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""View errors in the HTML code of a Modelica .mo file

The script will
* collect all the HTML code (<html>...</html>) in the Modelica file and
* print out the original code with line numbers as well as
* the tidy version of the code (with line numbers).
* tidylib will look for errors and present the respective line numbers.

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


class HTML_Tidy(CI_conf_class):
    """Class to Check Packages and run CheckModel Tests"""

    def __init__(self, package, correct_overwrite, correct_backup, log, font, align, correct_view,
                 library, wh_library):
        self.package = package
        self.correct_overwrite = correct_overwrite
        self.correct_backup = correct_backup
        self.log = log
        self.font = font
        self.align = align
        self.correct_view = correct_view
        self.library = library
        self.wh_library = wh_library
        super().__init__()

    def _get_html_model(self):
        library_list = self._get_library_model()
        wh_library_list = self._get_wh_library_model()
        html_model_list = self._remove_whitelist_model(library_list=library_list, wh_library_list=wh_library_list)
        return html_model_list

    def _check_arguments(self, root_dir):
        top_package = os.path.join(root_dir, "package.mo")
        if not os.path.isfile(top_package):
            raise ValueError("Argument rootDir=%s is not a Modelica package. Expected file '%s'." % (root_dir, top_package))

    def _print_html_error(self, model, htmlList, docCorrStr, errors):
        print('\n' + "----" + model + "----")
        print("\n-------- HTML Code --------")
        print(f"\n{self.number_print_List(htmlList)}")
        print(self.green + "\n-------- Corrected Code --------" + self.CEND)
        print(f"\n{docCorrStr}")
        print(self.CRED + "\n-------- Errors --------" + self.CEND)
        print(f"\n{errors}")

    def run_files(self):
        """
        Make sure that the parameter rootDir points to a Modelica package.
        Write error to error message
        Returns:
        """
        root_dir = self.package.replace(".", os.sep)
        self._check_arguments(root_dir=root_dir)
        err_msg = list()
        file_counter = 0
        html_model_list = self._get_html_model()
        for model in html_model_list:
            model_file = f'{model[:model.rfind(".mo")].replace(".", os.sep)}.mo'
            err, document_corr = self._check_file(model_file=model_file)
            if err is not "":
                err_msg.append("[-- %s ]\n%s" % (model, err))
            if self.correct_backup:
                self._backup_old_files(model_file=model_file, document_corr=document_corr, file_counter=file_counter)
            if self.correct_overwrite:
                self._correct_overwrite(model, document_corr)
                continue
            if self.correct_view:
                htmlList = self.getInfoRevisionsHTML(model)
                htmlStr = self.join_body(htmlList=htmlList, substitutions_dict={'\\"': '"'})
                document_corr, errors = self._htmlCorrection(htmlStr)
                doc_corr_str = self.number_print_List(document_corr.split('\n'), sep='\n')
                if len(errors) > 0 and errors.find("Warning: The summary attribute on the <table> element is obsolete in HTML5") == -1:
                    self._print_html_error(model=model, htmlList=htmlList, docCorrStr=doc_corr_str, errors=errors)
                    continue
                else:
                    continue
        if self.log:
            file = self._return_logfile(err_message=err_msg, root_dir=root_dir)
            err_list = self.read_logFile(file=file)
            self._write_exit(err_list=err_list)
            variable = self._write_result(err_list=err_list)
            exit(variable)

    def number_print_List(self, htmlList: list, sep: str = '') -> None:
        """
        Print a list of strings with line numbers
		Should be extended by a feature to highlight a given set of line
		numbers. This can help the reader to quickly identify the lines
		with errors.

		Parameters
		----------
		htmlList : list of str
				The html code - each line a list entry.
		sep : str
				String that seperates the line number from the line text.
		"""
        return sep.join(['{0:>5d} {1}'.format(i, line) for i, line in enumerate(htmlList)])

    def join_body(self, htmlList: list, substitutions_dict: dict = {'\\"': '"'}) -> str:
        """Joins a list of strings into a single string and makes replacements
		Parameters
		----------
		htmlList : list of str
				The html code - each line a list entry.
		substitutions_dict : dict
				A dictionary with key:value pairs for old and new text.
				The html code is escaped in Modelica. To feed it to tidylib
				we need to remove the escape characters.
		Returns
		-------
		str
				The html code as one string, cleared from escape characters.
		"""
        body = ''.join(htmlList)  # just glue it together again
        body = HTML_Tidy.make_string_replacements(
            self, theString=body, substitutions_dict={'\\"': '"'})
        return body

    def make_string_replacements(self, theString: str, substitutions_dict: dict = {'\\"': '"'}) -> str:
        """Takes a string and replaces according to a given dictionary
		Parameters
		----------
		theString : str
				The string that contains replaceble text.
		substitutions_dict : dict
				A dictionary with key:value pairs for old and new text.
		Returns
		-------
		str
				The modified string. """
        for k, v in substitutions_dict.items():
            theString = theString.replace(k, v)
        return theString

    def getInfoRevisionsHTML(self, moFile):
        """Returns a list that contains the html code
		This function returns a list that contain the html code of the
		info and revision sections. Each element of the list
		is a string.
		Parameters
		----------
		moFile : str
				The name of a Modelica source file.
		Returns
		-------
		The list of strings of the info and revisions section. """

        with open(moFile, mode="r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        nLin = len(lines)
        isTagClosed = True
        entries = list()
        for i in range(nLin):
            if isTagClosed:  # search for opening tag
                idxO = lines[i].find("<html>")
                if idxO > -1:  # search for closing tag on same line as opening tag
                    idxC = lines[i].find("</html>")
                    if idxC > -1:
                        entries.append(lines[i][idxO + 6:idxC] + '\n')
                        isTagClosed = True
                    else:
                        entries.append(lines[i][idxO + 6:])
                        isTagClosed = False
            else:  # search for closing tag
                idxC = lines[i].find("</html>")
                if idxC == -1:  # closing tag not found, copy full line
                    entries.append(lines[i])
                else:  # search for opening tag on same line as closing tag
                    entries.append(lines[i][0:idxC] + '\n')  # found closing tag, copy beginning of line only
                    isTagClosed = True
                    idxO = lines[i].find("<html>")
                    if idxO > -1:
                        entries.append(lines[i][idxO + 6:])
                        isTagClosed = False
        return entries

    def _correct_overwrite(self, moFulNam,
                           document_corr):  # This function overwrites the old modelica files with the corrected files
        os.remove(moFulNam)
        newfile = open(moFulNam, "w+b")
        newfile.write(document_corr.encode("utf-8"))

    def _backup_old_files(self, model_file, document_corr, file_counter):
        """
        This function backups the root folder and creates the corrected files
        Args:
            moFulNam:
            document_corr:
            file_counter:
        """
        root_dir = self.package.replace(".", os.sep)
        if os.path.exists(root_dir + "_backup") is False and file_counter == 1:
            shutil.copytree(root_dir, root_dir + "_backup")
            print("you can find your backup under " + root_dir + "_backup")
        os.remove(model_file)
        newfile = open(model_file, "w+b")
        newfile.write(document_corr.encode("utf-8"))

    def _return_logfile(self, err_message, root_dir):
        """
        This function creates the logfile
        Args:
            err_message:
            root_dir:

        Returns:

        """
        try:
            file = f'{root_dir}{os.sep}HTML-logfile.txt'
            print(f'Logfile is saved in {file}')
            log_file = open(f'{file}', "w")
            if len(err_message) >= 0:
                for error in err_message:
                    log_file.write(error + '\n')
            log_file.close()
            return file

        except IOError:
            print(f'Error: File {root_dir}{os.sep}HTML-logfile.txt does not exist.')
            exit(1)

    def read_logFile(self, file):
        """
        read logfile for possible errors
        Args:
            file:
        Returns:
        """
        log_file = open(file, "r")
        lines = log_file.readlines()
        log_file.close()
        err_list = []
        for line in lines:
            line = line.replace("\n", "")
            if line.find("Warning: The summary attribute on the <table> element is obsolete in HTML5") > -1:
                err_list.append(line)
                continue
            if self.font is True:
                if line.find("Warning: <font> element removed from HTML5") > -1:
                    err_list.append(line)
                    continue
            if self.align is True:
                if line.find('Warning: <p> attribute "align" not allowed for HTML5') > -1:
                    err_list.append(line)
                    continue
            if line.find("--") > -1 and line.find(".mo") > -1:
                continue
            if line.find('Warning: <img> lacks "alt" attribute') > -1:
                continue
            elif line.find("Warning") > -1:
                err_list.append(line)
        return err_list

    def _write_result(self, err_list):
        if len(err_list) > 0:
            variable = 1
        else:
            variable = 0
        return variable

    def _write_exit(self, err_list):
        try:
            exit_file = open(self.config_ci_exit_file, "w")
            if len(err_list) > 0:
                print("Syntax Error: Check HTML-logfile")
                exit_file.write("exit 1")
            else:
                print(f'HTML Check was successful!')
                exit_file.write("exit 0")
            exit_file.close()
        except IOError:
            print(f'Error: File {self.config_ci_exit_file} does not exist.')



    def _check_file(self, model_file):
        """
        This function returns a list that contain the html code of the
		info and revision sections. Each element of the list
		is a string.

		:param model_file: The name of a Modelica source file.
		:return: list The list of strings of the info and revisions section.
        Args:
            model_file:
        Returns:
        """
        with io.open(model_file, mode="r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        nLin = len(lines)
        isTagClosed = True
        code = list()
        htmlCode = list()
        errors = list()
        for i in range(nLin):
            if isTagClosed:  # search for opening tag
                idxO = lines[i].find("<html>")
                if idxO > -1:  # if found opening tag insert everything up to opening tag into the code list
                    code.append(lines[i][:idxO + 6])  # search for closing tag on same line as opening tag
                    idxC1 = lines[i].find("</html>")
                    idxC2 = lines[i].find(
                        "<\html>")  # check for both, correct and incorrect html tags, because dymola except also <\html>
                    if idxC1 > -1:
                        idxC = idxC1
                    elif idxC2 > -1:
                        idxC = idxC2
                    else:
                        idxC = -1
                    if idxC > -1:
                        htmlCode.append(lines[i][idxO + 6:idxC] + '\n')
                        code.append(HTML_Tidy._htmlCorrection(self, htmlCode)[0])
                        errors.append(HTML_Tidy._htmlCorrection(self, htmlCode)[1])
                        code.append(lines[i][idxC:])
                        isTagClosed = True
                    else:
                        htmlCode.append(lines[i][idxO + 6:])
                        isTagClosed = False
                else:
                    code.append(lines[i])
                    isTagClosed = True
            else:  # check for both, correct and incorrect html tags, because dymola except also <\html>
                idxC1 = lines[i].find("</html>")
                idxC2 = lines[i].find("<\html>")
                if idxC1 > -1:
                    idxC = idxC1
                elif idxC2 > -1:
                    idxC = idxC2
                else:
                    idxC = -1
                if idxC > -1:
                    htmlCode.append(lines[i][idxO + 6:idxC])
                    code.append(self._htmlCorrection(htmlCode)[0])
                    errors.append(self._htmlCorrection(htmlCode)[1])
                    code.append(lines[i][idxC:])
                    htmlCode = list()
                    idxO = lines[i].find("<html>")
                    if idxO > -1:
                        isTagClosed = False
                    else:
                        isTagClosed = True
                else:
                    htmlCode.append(lines[i])
                    isTagClosed = False
        document_corr = ""
        if len(code) > 0:
            for lines in code:
                document_corr += lines
        errors_string = ""
        if len(errors) > 0:
            for lines in errors:
                errors_string += lines
        document_corr_img = ""
        CloseFound = True
        for line in document_corr.splitlines():
            line, CloseFound = HTML_Tidy.correct_table_summary(self, line, CloseFound)
            if self.font == True:
                line, CloseFound = HTML_Tidy.correct_font(
                    self, line, CloseFound)
            if self.align == True:
                line, CloseFound = HTML_Tidy.correct_p_align(
                    self, line, CloseFound)
            document_corr_img += line + '\n'
        return document_corr_img, errors_string

    def _htmlCorrection(self, html_code):
        """
        Args:
            html_code ():
        Returns:
        """
        substitutions_dict: dict = {'"': '\\"', '<br>': '<br/>', '<br/>': '<br/>'}
        html_str = self.join_body(htmlList=html_code, substitutions_dict={'\\"': '"'})

        html_correct, errors = tidy_document(f"{html_str}",
                                             options={'doctype': 'html5',
                                                      'show-body-only': 1,
                                                      'numeric-entities': 1,
                                                      'output-html': 1,
                                                      'wrap': 72,
                                                      'alt-text': '', })
        document_corr = self.make_string_replacements(theString=html_correct,
                                                      substitutions_dict=substitutions_dict)
        return document_corr, errors

    def correct_table_summary(self, line, CloseFound):
        """
        delete Summary in table and add <caption> Text </caption>
        Args:
            line ():
            CloseFound ():

        Returns:

        """
        if CloseFound == True:
            tableTag = line.encode("utf-8").find(b"<table")
            sumTag = line.encode("utf-8").find(b"summary")
            CloseTagIntex = line.encode("utf-8").rfind(b'">')
            if tableTag > -1 and sumTag > -1:
                line = line[:sumTag] + "> " + \
                       line[sumTag:].replace('summary=', '<caption>', 1)
                line = (line.replace('">', '</caption>', 1))
        return line, CloseFound

    def correct_th_align(self, line, CloseFound):
        """
        Correct algin with th and replace style="text-align"
        Args:
            line ():
            CloseFound ():

        Returns:

        """
        if CloseFound == True:
            alignTag = line.encode("utf-8").find(b"align")
            thTag = line.encode("utf-8").find(b"th")
            CloseTagIntex = line.encode("utf-8").rfind(b'">')
            if alignTag > -1 and thTag > -1:
                line = (line.replace('\\', ''))
        return line, CloseFound

    def correct_p_align(self, line, CloseFound):
        """
        Correct align in p and replace style="text-align"
        Args:
            line ():
            CloseFound ():

        Returns:

        """
        # Wrong: <p style="text-align:center;">
        # Correct: <p style="text-align:center;">
        # Correct: <p style="text-align:center;font-style:italic;color:blue;">k = c<sub>p</sub>/c<sub>v</sub> </p>
        # Correct: <p style="text-align:center;font-style:italic;">
        if CloseFound == True:
            pTag = line.encode("utf-8").find(b"<p")
            alignTag = line.encode("utf-8").find(b"align")
            etag = line.encode("utf-8").find(b"=")
            closetag = line.encode("utf-8").find(b">")
            styleTag = line.encode("utf-8").find(b"text-align:")
            style = line.encode("utf-8").find(b"style")
            rstyle = style = line.encode("utf-8").find(b"style")
            StyleCount = line.count("style=")
            if styleTag > -1:
                return line, CloseFound
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
        return line, CloseFound

    def correct_font(self, line, CloseFound):
        """
        Replace font to style für html5
        Args:
            line ():
            CloseFound ():

        Returns:

        """
        if CloseFound == True:
            styleTag_1 = line.encode("utf-8").find(b"style=")
            styleTag_2 = line.encode("utf-8").find(b"color")
            fontTag = line.encode("utf-8").find(b"<font")
            rfontTag = line.encode("utf-8").rfind(b"</font>")
            firstCloseTage = line.encode("utf-8").find(b">")
            etag = line.encode("utf-8").find(b"=")
            if styleTag_1 > -1 and styleTag_2 > -1:
                if fontTag > -1 and rfontTag > -1:
                    sline = (line[fontTag:rfontTag].replace('\\', ''))
                    sline = sline.replace('"', '')
                    sline = sline.replace('<font', '<span')
                    sline = (sline.replace('color:', '"color:'))
                    sline = sline.replace(';>', '">')
                    line = line[:fontTag] + sline + \
                           line[rfontTag:].replace('</font>', '</span>')
            elif fontTag > -1 and rfontTag > -1:
                sline = (line[fontTag:rfontTag].replace('\\', ''))
                sline = sline.replace('"', '')
                sline = sline.replace('<font', '<span')
                sline = (sline.replace('color=', 'style="color:'))
                sline = (sline.replace('>', '">'))
                line = line[:fontTag] + sline + \
                       line[rfontTag:].replace('</font>', '</span>')
        return line, CloseFound

    def correct_img_atr(self, line, CloseFound):
        """
        Correct img and check for missing alt attributed
        Args:
            line ():
            CloseFound ():

        Returns:

        """
        if CloseFound == True:
            imgTag = line.encode("utf-8").find(b"img")
            if imgTag > -1:
                imgCloseTagIndex = line.find(">", imgTag)
                imgAltIndex = line.find("alt", imgTag)
                if imgCloseTagIndex > -1 and imgAltIndex == -1:  # if close tag exists but no alt attribute, insert alt attribute and change > to />
                    line = line[:imgTag] + \
                           line[imgTag:].replace(">", ' alt="" />', 1)
                    CloseFound = True
                elif imgCloseTagIndex > -1 and imgAltIndex > -1:  # if close tag exists and alt attribute exists, only change > to />
                    line = line[:imgTag] + line[imgTag:].replace(">", ' />', 1)
                    CloseFound = True

                elif imgCloseTagIndex == -1:  # if close tag is not in the same line
                    line = line
                    CloseFound = False
        else:  # if no close tag was found in previous line, but opening tag found search for close on this line with same
            imgCloseTagIndex = line.find(">")
            imgAltIndex = line.find("alt")
            if imgCloseTagIndex > -1 and imgAltIndex == -1:
                line = line[:imgCloseTagIndex] + \
                       line[imgCloseTagIndex:].replace(">", ' alt="" />', 1)
                CloseFound = True
            elif imgCloseTagIndex > -1 and imgAltIndex > -1:
                line = line[:imgCloseTagIndex] + \
                       line[imgCloseTagIndex:].replace(">", ' />', 1)
                CloseFound = True
            elif imgCloseTagIndex == -1:
                CloseFound = False
                line = line
        return line, CloseFound

    def delete_html_revision(self, line, CloseFound):
        """
        Delete revsion
        Args:
            line ():
            CloseFound ():

        Returns:

        """
        if CloseFound == True:
            htmlTag = line.encode("utf-8").find(b"</html>")
            htmlCloseTag = line.encode("utf-8").find(b"<html>")
            RevTag = line.encode("utf-8").find(b"revision")
            if htmlTag > -1 and RevTag > -1:
                if htmlCloseTag > -1:
                    line = ""
        return line, CloseFound

    def _list_all_model(self):
        """

        Returns:
        """
        library_list = []
        wh_library_list = []
        try:
            rootdir = self.package.replace(".", os.sep)
            file = open(self.wh_html_file, "r")
            lines = file.readlines()
            for line in lines:
                if line.find(".mo") > -1:
                    line = line.replace(self.wh_library, self.library)
                    line = line.replace("\n", "")
                    wh_library_list.append(line)
            file.close()
            for subdir, dirs, files in os.walk(rootdir):  # Return library models
                for file in files:
                    filepath = subdir + os.sep + file
                    if filepath.endswith(".mo"):
                        model = filepath.replace(os.sep, ".")
                        model = model[model.rfind(self.library):]
                        library_list.append(model)
            return library_list, wh_library_list
        except IOError:
            print(f'Error: File {self.wh_html_file} does not exist. Check without a whitelist.')
            return library_list, wh_library_list

    def _get_wh_library_model(self):
        """
        Returns:
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
         Return library models
        Returns:

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

    def _remove_whitelist_model(self, library_list, wh_library_list):
        """
        get library model
        Returns:
        """
        remove_models_list = []
        for model in library_list:
            for wh_model in wh_library_list:
                if model == wh_model:
                    remove_models_list.append(model)
        for remove_model in remove_models_list:
            library_list.remove(remove_model)
        return library_list


class HTML_whitelist(CI_conf_class):

    def __init__(self, wh_library, git_url):
        self.wh_library = wh_library
        self.git_url = git_url
        super().__init__()

    def create_whitelist(self):  # Create a new whiteList
        Repo.clone_from(self.git_url, self.wh_library)
        model_list = []
        for subdir, dirs, files in os.walk(self.wh_library):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo"):
                    model = filepath.replace(os.sep, ".")
                    model = model[model.rfind(self.wh_library):model.rfind(".mo")]
                    model_list.append(model)
        file = open(self.wh_html_file, "w")
        for model in model_list:
            file.write("\n" + model + ".mo" + "\n")
        file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run HTML correction on files, print found errors or backup old files')
    parser.add_argument("--correct-overwrite", action="store_true", default=False,
                        help="correct html code in modelica files and overwrite old files")
    parser.add_argument("--correct-backup", action="store_true", default=False,
                        help="correct html code in modelica "  "files and backup old files")
    parser.add_argument("--log", action="store_true",
                        default=False, help="print logfile of errors found")
    parser.add_argument('-s', "--single-package", metavar="AixLib.Package",
                        help="Test only the Modelica package AixLib.Package")
    parser.add_argument("-p", "--path", default=".",
                        help="Path where top-level package.mo of the library is located")
    parser.add_argument("--font", action="store_true", default=False,
                        help="correct html code: Remove font to span")
    parser.add_argument("--align", action="store_true", default=False,
                        help="correct html code: Remove align  to style=text-algin:")
    parser.add_argument("--WhiteList", action="store_true", default=False,
                        help="Create a new WhiteList Library IBPSA")
    parser.add_argument("--correct-view", action="store_true", default=False,
                        help="Print the Correct HTML Code")
    parser.add_argument("-L", "--library", default="AixLib", help="Library to test")
    parser.add_argument("--wh_library", default="IBPSA", help="Library on whitelist")
    parser.add_argument("--git-url", default="https://github.com/ibpsa/modelica-ibpsa.git", help="url repository")
    parser.add_argument("--filter", default=False, action="store_true")

    args = parser.parse_args()
    conf = CI_conf_class()
    conf.check_ci_folder_structure(folders_list=[conf.config_ci_dir])
    conf.check_ci_file_structure(files_list=[conf.config_ci_exit_file])
    HTML_Check = HTML_Tidy(package=args.single_package,
                           correct_overwrite=args.correct_overwrite,
                           correct_backup=args.correct_backup,
                           log=args.log,
                           font=args.font,
                           align=args.align,
                           correct_view=args.correct_view,
                           library=args.library,
                           wh_library=args.wh_library)
    if args.correct_backup is True:
        print("Create a Backup")
        HTML_Check.run_files()
        var = HTML_Check.run_files()
        print(var)
    elif args.correct_overwrite is True:
        print("Overwrite the Library")
        var = HTML_Check.run_files()
        HTML = HTML_Tidy(package=args.single_package,
                         correct_overwrite=args.correct_overwrite,
                         correct_backup=args.correct_backup,
                         log=False,
                         font=args.font,
                         align=args.align,
                         correct_view=args.correct_view,
                         library=args.library,
                         wh_library=args.wh_library)
        HTML.run_files()
    elif args.correct_view is True:
        print("Print the Correct HTML Code")
        HTML_Check.run_files()
    elif args.WhiteList is True:
        whitelist = HTML_whitelist(wh_library=args.wh_library, git_url=args.git_url)
        print(f'Create a whitelist of {args.wh_library} Library')
        whitelist.create_whitelist()
    elif args.correct_overwrite is False and args.correct_backup is False and args.log is False and args.correct_view is False:
        print("please use -h or --help for help")
