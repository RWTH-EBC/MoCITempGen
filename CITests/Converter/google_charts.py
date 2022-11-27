import argparse
import os
import shutil
import sys
import pandas as pd
from mako.template import Template
sys.path.append('Dymola_python_tests/CITests/CI_Configuration')
from configuration import CI_conf_class


class Plot_Charts(CI_conf_class):

    def __init__(self, template, package, library):
        """
        Args:
            template (): mako template class
            package (): package to plot
            library (): library to plot
        init:
            self.f_log ():  path for unitTest-dymola.log, important for errors
            self.temp_chart_path (): path for every single package
        """
        self.package = package
        self.library = library
        self.template = template
        super().__init__()
        self.f_log = f'{self.library}{os.sep}unitTests-dymola.log'
        self.csv_file = f'reference.csv'
        self.test_csv = f'test.csv'
        self.temp_chart_path = f'{self.chart_dir}{os.sep}{self.package}'
        self.funnel_path = f'{self.library}{os.sep}funnel_comp'
        self.ref_path = f'{self.library}{os.sep}Resources{os.sep}ReferenceResults{os.sep}Dymola'
        self.index_html_file = f'{self.temp_chart_path}{os.sep}index.html'


    @staticmethod
    def _check_ref_file(reference_file_list):
        """
        Args:
            reference_file_list ():
        Returns:
        """
        update_ref_list = []
        for reference_file in reference_file_list:
            if os.path.isfile(reference_file) is False:
                print(f'File {reference_file} does not exist.')
                continue
            else:
                update_ref_list.append(reference_file)
                print(f'\nCreate plots for reference result {reference_file}')
        return update_ref_list

    def write_html_plot_templates(self, reference_file_list):
        """
        Args:
            reference_file_list ():
        """
        new_ref_list = self._check_ref_file(reference_file_list=reference_file_list)
        for reference_file in new_ref_list:
            results = self._read_data(reference_file=reference_file)
            self._mako_line_html_new_chart(reference_file=reference_file, value_list=results[0], legend_list=results[1])
            continue

    def read_show_reference(self):
        """
        Returns:
        """
        if os.path.isfile(self.ci_interact_show_ref_file) is False:
            print(f'File {self.ci_interact_show_ref_file} directory does not exist.')
            exit(0)
        else:
            print(f'Plot results from file {self.ci_interact_show_ref_file}')
            file = open(self.ci_interact_show_ref_file, "r")
            lines = file.readlines()
            file.close()
            reference_file_list = []
            for line in lines:
                if len(line) == 0:
                    continue
                else:
                    reference_file_list.append(f'{self.ref_path}{os.sep}{line.strip()}')
                    continue
            if len(reference_file_list) == 0:
                print(
                    f'No reference files in file {self.ci_interact_show_ref_file}. Please add here your reference files you want to '
                    f'update')
                exit(0)
            else:
                return reference_file_list

    @staticmethod
    def _read_data(reference_file):
        """
        Read Reference results in AixLib\Resources\ReferenceResults\Dymola\…
        Args:
            reference_file ():
        Returns:
        """
        time_int = []
        legend_list = []
        value_list = []
        distriction_values = {}
        time_interval_list = []
        time_interval_steps = int
        for line in open(reference_file, 'r'):
            current_value = []
            if line.find("last-generated=") > -1 or line.find("statistics-simulation=") > -1 or line.find(
                    "statistics-initialization=") > -1:
                continue
            elif line.find("time=") > -1:
                time_int = line.split("=")[1]
                time_int = time_int.split(",")
                continue
            if line.find("=") > -1:
                values = line.split("=")
                if len(values) < 2:
                    continue
                legend = values[0]
                numbers = values[1]
                time_interval_steps = len(numbers.split(","))
                distriction_values[legend] = numbers
                legend_list.append(legend)
                number = numbers.split(",")
                for n in number:
                    value = n.replace("[", "").lstrip()
                    value = value.replace("]", "")
                    value = float(value)
                    current_value.append(value)
                value_list.append(current_value)
                continue
        first_time_interval = float((time_int[0].replace("[", "").lstrip()))
        last_time_interval = float((time_int[len(time_int) - 1].replace("]", "").lstrip()))
        time_interval = last_time_interval / time_interval_steps
        time = first_time_interval
        for step in range(1, time_interval_steps + 1, 1):
            if time == first_time_interval:
                time_interval_list.append(time)
                time = time + time_interval
            elif step == time_interval_steps:
                time = time + time_interval
                time_interval_list.append(time)
            else:
                time_interval_list.append(time)
                time = time + time_interval
        value_list.insert(0, time_interval_list)
        value_list = list(map(list, zip(*value_list)))
        return value_list, legend_list

    def get_updated_reference_files(self):
        """
        Returns:
        """
        if os.path.isfile(self.ci_interact_update_ref_file) is False:
            print(f'File {self.ci_interact_update_ref_file} directory does not exist.')
            exit(0)
        else:
            print(f'Plot results from file {self.ci_interact_update_ref_file}')
        file = open(self.ci_interact_update_ref_file, "r")
        lines = file.readlines()
        reference_list = []
        for line in lines:
            line = line.strip()
            if line.find(".txt") > -1 and line.find("_"):
                reference_list.append(f'{self.ref_path}{os.sep}{line.strip()}')
                continue
        file.close()
        return reference_list

    def get_new_reference_files(self):
        """
        Returns:
        """
        if os.path.isfile(self.config_ci_new_create_ref_file) is False:
            print(f'File {self.config_ci_new_create_ref_file} directory does not exist.')
            exit(0)
        else:
            print(f'Plot results from file {self.config_ci_new_create_ref_file}')
        file = open(self.new_ref_file, "r")
        lines = file.readlines()
        reference_list = []
        for line in lines:
            line = line.strip()
            if line.find(".txt") > -1 and line.find("_"):
                reference_list.append(f'{line.strip()}')
                continue
        return reference_list

    @staticmethod
    def get_values(reference_list):
        """
        Args:
            reference_list ():
        Returns:
        """
        reference_file = open(f'{reference_list}', "r")
        lines = reference_file.readlines()
        reference_file.close()
        measure_list = []
        measure_len = int
        time_str = str
        for line in lines:  # searches for values and time intervals
            if line.find("last-generated=") > -1:
                continue
            if line.find("statistics-simulation=") > -1:
                continue
            if line.split("="):
                line = line.replace("[", "")
                line = line.replace("]", "")
                line = line.replace("'", "")
                values = (line.replace("\n", "").split("="))
                if len(values) < 2:
                    continue
                else:
                    legend = values[0]
                    measures = values[1]
                    if legend.find("time") > -1:
                        time_str = f'{legend}:{measures}'
                    else:
                        measure_len = len(measures.split(","))
                        measure_list.append(f'{legend}:{measures}')
        return time_str, measure_list, measure_len

    @staticmethod
    def _get_time_int(time_list, measure_len):
        """
        Args:
            time_list ():
            measure_len ():
        Returns:
        """
        time_val = time_list.split(":")[1]
        time_beg = time_val.split(",")[0]
        time_end = time_val.split(",")[1]
        time_int = float(time_end) - float(time_beg)
        tim_seq = time_int / float(measure_len)
        time_num = float(time_beg)
        time_list = []
        for time in range(0, measure_len + 1):
            time_list.append(time_num)
            time_num = time_num + tim_seq
        return time_list

    def read_unitTest_log(self):
        """
        Read unitTest_log from regressionTest, write variable and model name with difference
        Returns:
        """
        try:
            self.check_file(file=self.f_log)
            log_file = open(self.f_log, "r")
            lines = log_file.readlines()
            model_variable_list = []
            for line in lines:
                if line.find("*** Warning:") > -1:
                    if line.find(".mat") > -1:
                        model = line[line.find("Warning:") + 9:line.find(".mat")]
                        var = line[line.find(".mat:") + 5:line.find("exceeds ")].lstrip()
                        model_variable_list.append(f'{model}:{var}')
                    if line.find("*** Warning: Numerical Jacobian in 'RunScript") > -1 and line.find(".mos") > -1:
                        model = line[line.rfind(os.sep) + 1:line.find(".mos")].lstrip()
                        var = ""
                        model_variable_list.append(f'{model}:{var}')
                    if line.find(
                            "*** Warning: Failed to interpret experiment annotation in 'RunScript") > -1 and line.find(
                            ".mos") > -1:
                        model = line[line.rfind(os.sep) + 1:line.find(".mos")].lstrip()
                        var = ""
                        model_variable_list.append(f'{model}:{var}')
            return model_variable_list
        except IOError:
            print(f'Error: File {self.f_log} does not exist.')
            exit(1)

    def get_ref_file(self, model):
        """
        Args:
            model ():
        Returns:
        """
        for file in os.listdir(self.ref_path):
            if file.find(model) > -1:
                return file
            else:
                continue

    def _read_csv_funnel(self, url):
        """
        Read the differenz variables from csv_file and test_file
        Args:
            url ():

        Returns:

        """
        csv_file = f'{url.strip()}{os.sep}{self.csv_file}'
        test_csv = f'{url.strip()}{os.sep}{self.test_csv}'
        try:
            var_model = pd.read_csv(csv_file)
            var_test = pd.read_csv(test_csv)
            temps = var_model[['x', 'y']]
            d = temps.values.tolist()
            test_tmp = var_test[['x', 'y']]
            e = test_tmp.values.tolist()
            e_list = []
            for i in range(0, len(e)):
                e_list.append((e[i][1]))
            results = zip(d, e_list)
            result_set = list(results)
            value_list = []
            for i in result_set:
                i = str(i)
                i = i.replace("(", "")
                i = i.replace("[", "")
                i = i.replace("]", "")
                i = i.replace(")", "")
                value_list.append("[" + i + "]")
            return value_list
        except pd.errors.EmptyDataError:
            print(f'{csv_file} is empty')

    def check_folder_path(self):
        """

        """
        if os.path.isdir(self.funnel_path) is False:
            print(f'Funnel directory does not exist.')
        else:
            print(f'Search for results in {self.funnel_path}')
        if os.path.isdir(self.temp_chart_path) is False:
            os.mkdir(self.temp_chart_path)
            print(f'Save plot in {self.temp_chart_path}')
        if os.path.isdir(self.chart_dir) is False:
            os.mkdir(self.chart_dir)

    def mako_line_html_chart(self, model, var):
        """
        Load and read the templates, write variables in the templates
        Args:
            model ():
            var ():
        """
        if var == "":
            path_list = os.listdir((f'{self.library}{os.sep}funnel_comp'.strip()))
            for file in path_list:
                if file[:file.find(".mat")] == model:
                    path_name = f'{self.library}{os.sep}funnel_comp{os.sep}{file}'.strip()
                    var = file[file.find(".mat") + 5:]
                    if os.path.isdir(path_name) is False:
                        print(
                            f'Cant find folder: {self.CRED}{model}{self.CEND} with variable {self.CRED}{var}{self.CEND}')
                    else:
                        print(f'Plot model: {self.green}{model}{self.CEND} with variable:{self.green} {var}{self.CEND}')
                        value = self._read_csv_funnel(url=path_name)
                        my_template = self.template(filename=self.temp_chart_file)
                        html_chart = my_template.render(values=value,
                                                        var=[f'{var}_ref', var],
                                                        model=model,
                                                        title=f'{model}.mat_{var}')
                        file_tmp = open(f'{self.temp_chart_path}{os.sep}{model}_{var.strip()}.html', "w")
                        file_tmp.write(html_chart)
                        file_tmp.close()
        else:
            path_name = (f'{self.library}{os.sep}funnel_comp{os.sep}{model}.mat_{var}'.strip())
            if os.path.isdir(path_name) is False:
                print(f'Cant find folder: {self.CRED}{model}{self.CEND} with variable {self.CRED}{var}{self.CEND}')
            else:
                print(f'Plot model: {self.green}{model}{self.CEND} with variable:{self.green} {var}{self.CEND}')
                value = self._read_csv_funnel(url=path_name)
                my_template = self.template(filename=self.temp_chart_file)
                html_chart = my_template.render(values=value,
                                                var=[f'{var}_ref', var],
                                                model=model,
                                                title=f'{model}.mat_{var}')
                file_tmp = open(f'{self.temp_chart_path}{os.sep}{model}_{var.strip()}.html', "w")
                file_tmp.write(html_chart)
                file_tmp.close()

    def _mako_line_html_new_chart(self, reference_file, value_list, legend_list):
        """
        Load and read the templates, write variables in the templates
        Args:
            reference_file ():
            value_list ():
            legend_list ():
        """
        if os.path.isfile(reference_file) is False:
            print(
                f'Cant find folder: {self.CRED}{reference_file[reference_file.rfind(os.sep) + 1:]}{self.CEND} with variables: {self.CRED}{legend_list}{self.CEND}')
        else:
            print(
                f'Plot model: {self.green}{reference_file[reference_file.rfind(os.sep) + 1:]}{self.CEND} with variables:\n{self.green}{legend_list}{self.CEND}\n')
            my_template = self.template(filename=self.temp_chart_file)
            html_chart = my_template.render(values=value_list,
                                            var=legend_list,
                                            model=reference_file,
                                            title=reference_file)
            file_tmp = open(
                f'{self.temp_chart_path}{os.sep}{reference_file[reference_file.rfind(os.sep):].replace(".txt", ".html")}', "w")
            file_tmp.write(html_chart)
            file_tmp.close()

    def mako_line_ref_chart(self, model, var):
        """
        Load and read the templates, write variables in the templates
        Args:
            model ():
            var ():
        """
        path_name = (f'{self.library}{os.sep}funnel_comp{os.sep}{model}.mat_{var}'.strip())
        folder_name = os.path.isdir(path_name)
        if folder_name is False:
            print(f'Cant find folder: {self.CRED}{model}{self.CEND} with variable {self.CRED}{var}{self.CEND}')
        else:
            print(f'Plot model: {self.green}{model}{self.CEND} with variable:{self.green} {var}{self.CEND}')
            value = self._read_csv_funnel(url=path_name)
            my_template = self.template(filename=self.temp_chart_file)
            html_chart = my_template.render(values=value,
                                            var=[f'{var}_ref', var],
                                            model=model,
                                            title=f'{model}.mat_{var}')
            file_tmp = open(f'{self.temp_chart_path}{os.sep}{model}_{var.strip()}.html', "w")
            file_tmp.write(html_chart)
            file_tmp.close()

    def create_index_layout(self):
        """
        Create an index layout from a template
        """
        html_file_list = []
        for file in os.listdir(self.temp_chart_path):
            if file.endswith(".html") and file != "index.html":
                html_file_list.append(file)
        my_template = self.template(filename=self.temp_index_file)
        if len(html_file_list) == 0:
            print(f'No html files')
            os.rmdir(self.temp_chart_path)
            exit(0)
        else:
            html_chart = my_template.render(html_model=html_file_list)
            file_tmp = open(self.index_html_file, "w")
            file_tmp.write(html_chart)
            file_tmp.close()
            print(f'Create html file with reference results.')

    def create_layout(self, temp_dir, layout_html_file):
        """
        Creates a layout index that has all links to the subordinate index files.
        """
        package_list = []
        for folders in os.listdir(temp_dir):
            if folders == "style.css" or folders == "index.html":
                continue
            else:
                package_list.append(folders)
        if len(package_list) == 0:
            print(f'No html files')
            exit(0)
        else:
            my_template = self.template(filename=self.temp_layout_file)
            html_chart = my_template.render(single_package=package_list)
            file_tmp = open(layout_html_file, "w")
            file_tmp.write(html_chart)
            file_tmp.close()

    @staticmethod
    def check_file(file):
        """

        Args:
            file ():
        """
        file_check = os.path.isfile(file)
        if file_check is False:
            print(f'{file} does not exists.')
            exit(1)
        else:
            print(f'{file} exists.')

    def get_funnel_comp(self):
        """

        Returns:

        """
        folders = os.listdir(self.funnel_path)
        return folders

    def delete_folder(self):
        """

        """
        if os.path.isdir(self.chart_dir) is False:
            print(f'Directory {self.chart_dir} does not exist.')
        else:
            folder_list = os.listdir(self.chart_dir)
            for folders in folder_list:
                if folders.find(".html") > -1:
                    os.remove(f'{self.chart_dir}{os.sep}{folders}')
                    continue
                else:
                    shutil.rmtree(f'{self.chart_dir}{os.sep}{folders}')

    def check_setting(self):
        """

        """
        if self.library is None:
            print(f'Please set a library (e.g. --library AixLib')
            exit(0)
        else:
            print(f'Setting library: {self.library}')
        if self.package is None:
            print(f'Please set a package (e.g. --single-package Airflow)')
            exit(0)
        else:
            print(f'Setting package: {self.package}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot diagramms')
    unit_test_group = parser.add_argument_group("arguments to plot diagrams")
    unit_test_group.add_argument("--line-html",
                                 help='plot a google html chart in line form',
                                 action="store_true")
    unit_test_group.add_argument("--create-layout",
                                 help='Create a layout with a plots',
                                 action="store_true")
    unit_test_group.add_argument("--line-matplot",
                                 help='plot a matlab chart ',
                                 action="store_true")
    unit_test_group.add_argument("--new-ref",
                                 help="Plot new models with new created reference files",
                                 action="store_true")
    unit_test_group.add_argument("-e", "--error",
                                 help='Plot only model with errors',
                                 action="store_true")
    unit_test_group.add_argument("--show-ref",
                                 help='Plot only model on the interact ci list',
                                 action="store_true")
    unit_test_group.add_argument("--update-ref",
                                 help='Plot only updated models',
                                 action="store_true")
    unit_test_group.add_argument("--show-package",
                                 help='Plot only updated models',
                                 action="store_true")
    unit_test_group.add_argument('-s', "--single-package",
                                 metavar="Modelica.Package",
                                 help="Test only the Modelica package Modelica.Package")
    unit_test_group.add_argument("-L", "--library", default="AixLib", help="Library to test")
    unit_test_group.add_argument('-fun', "--funnel-comp",
                                 help="Take the datas from funnel_comp",
                                 action="store_true")
    unit_test_group.add_argument('-ref', "--ref-txt",
                                 help="Take the datas from reference datas",
                                 action="store_true")
    args = parser.parse_args()
    conf = CI_conf_class()
    conf.check_ci_folder_structure(folders_list=[conf.chart_dir, conf.temp_chart_dir])
    conf.check_ci_file_structure(files_list=[conf.temp_chart_file, conf.temp_index_file, conf.temp_layout_file])
    charts = Plot_Charts(template=Template, package=args.single_package, library=args.library)
    if args.line_html is True:
        charts.check_setting()
        charts.delete_folder()
        charts.check_folder_path()
        if args.error is True:
            model_var_list = charts.read_unitTest_log()
            print(f'Plot line chart with different reference results.\n')
            for model_variable in model_var_list:
                model_variable = model_variable.split(":")
                if args.funnel_comp is True:
                    charts.mako_line_html_chart(model=model_variable[0], var=model_variable[1])
                    pass
                if args.ref_txt is True:
                    ref_file = charts.get_ref_file(model=model_variable[0])
                    if ref_file is None:
                        print(f'Reference file for model {model_variable[0]} does not exist.')
                        continue
                    else:
                        result = charts.get_values(reference_list=ref_file)
                        charts.mako_line_ref_chart(model=model_variable[0], var=model_variable[1])
        if args.new_ref is True:
            ref_list = charts.get_new_reference_files()
            charts.write_html_plot_templates(reference_file_list=ref_list)
            pass
        if args.update_ref is True:
            ref_list = charts.get_updated_reference_files()
            charts.write_html_plot_templates(reference_file_list=ref_list)
            pass
        if args.show_ref is True:
            ref_list = charts.read_show_reference()
            charts.write_html_plot_templates(reference_file_list=ref_list)
            pass
        if args.show_package is True:
            folder = charts.get_funnel_comp()
            for ref in folder:
                if args.funnel_comp is True:
                    charts.mako_line_html_chart(model=ref[:ref.find(".mat")], var=ref[ref.rfind(".mat") + 5:])
            pass
        charts.create_index_layout()
        charts.create_layout(temp_dir=conf.chart_dir, layout_html_file=f'{conf.chart_dir}{os.sep}index.html')
    if args.create_layout is True:
        conf.check_ci_folder_structure(folders_list=[f'data{os.sep}plots'])
        charts.create_layout(temp_dir=f'data{os.sep}plots', layout_html_file=f'data{os.sep}plots{os.sep}index.html')
