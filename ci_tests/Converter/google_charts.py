import argparse
import os
import shutil
import pandas as pd
from mako.template import Template
from ci_test_config import ci_config
from ci_tests.structure.config_structure import data_structure
import sys
from pathlib import Path

class Plot_Charts(ci_config):

    def __init__(self,  package, library):
        """
        Args:
            package (): package to plot
            library (): library to plot
        init:
            self.f_log ():  path for unitTest-dymola.log, important for errors
            self.temp_chart_path (): path for every single package
        """
        self.package = package
        self.library = library
        super().__init__()
        self.f_log = Path(self.library, "unitTests-dymola.log")
        self.csv_file = Path("reference.csv")
        self.test_csv = Path("test.csv")
        self.temp_chart_path = Path(self.chart_dir, self.package)
        self.funnel_path = Path(self.library, "funnel_comp")
        self.ref_path = Path(self.library, self.library_ref_results_dir)
        self.index_html_file = Path(self.temp_chart_path, "index.html")

    @staticmethod
    def _check_ref_file(reference_file_list):
        """
        Args:
            reference_file_list ():
        Returns:
        """
        update_ref_list = list()
        for reference_file in reference_file_list:
            if os.path.isfile(reference_file) is False:
                print(f'File {reference_file} does not exist.')
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
            self._mako_line_html_new_chart(reference_file=reference_file,
                                           value_list=results[0],
                                           legend_list=results[1])
            continue

    def read_show_reference(self):
        """
        Returns:
        """
        if os.path.isfile(self.ci_interact_show_ref_file) is False:
            print(f'File {self.ci_interact_show_ref_file} does not exist.')
            exit(0)
        else:
            print(f'Plot results from file {self.ci_interact_show_ref_file}')
            with open(self.ci_interact_show_ref_file, "r") as file:
                lines = file.readlines()
            reference_file_list = list()
            for line in lines:
                if len(line) != 0:
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
        time_int = list()
        legend_list = list()
        value_list = list()
        distriction_values = {}
        time_interval_list = list()
        time_interval_steps = int
        with open(reference_file, 'r') as ref_file:
            lines = ref_file.readlines()
        for line in lines:
            current_value = list()
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
        with open(self.ci_interact_update_ref_file, "r") as file:
            lines = file.readlines()
        reference_list = list()
        for line in lines:
            line = line.strip()
            if line.find(".txt") > -1 and line.find("_"):
                reference_list.append(f'{self.ref_path}{os.sep}{line.strip()}')
                continue
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
        with open(self.config_ci_new_create_ref_file, "r") as file:
            lines = file.readlines()
        reference_list = list()
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
        with open(f'{reference_list}', "r") as reference_file:
            lines = reference_file.readlines()
        measure_list = list()
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
        time_list = list()
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
            with open(self.f_log, "r") as log_file:
                lines = log_file.readlines()
            model_variable_list = list()
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
        csv_file = Path(url.strip(), self.csv_file)
        test_csv = Path(url.strip(), self.test_csv)
        try:
            var_model = pd.read_csv(csv_file)
            var_test = pd.read_csv(test_csv)
            temps = var_model[['x', 'y']]
            d = temps.values.tolist()
            test_tmp = var_test[['x', 'y']]
            e = test_tmp.values.tolist()
            e_list = list()
            for i in range(0, len(e)):
                e_list.append((e[i][1]))
            results = zip(d, e_list)
            result_set = list(results)
            value_list = list()
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
            print(f'Search for reference result in {self.funnel_path}')
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
                        my_template = Template(filename=self.temp_chart_file)
                        html_chart = my_template.render(values=value,
                                                        var=[f'{var}_ref', var],
                                                        model=model,
                                                        title=f'{model}.mat_{var}')
                        with open(f'{self.temp_chart_path}{os.sep}{model}_{var.strip()}.html', "w") as file_tmp:
                            file_tmp.write(html_chart)
        else:
            path_name = (f'{self.library}{os.sep}funnel_comp{os.sep}{model}.mat_{var}'.strip())
            if os.path.isdir(path_name) is False:
                print(f'Cant find folder: {self.CRED}{model}{self.CEND} with variable {self.CRED}{var}{self.CEND}')
            else:
                print(f'Plot model: {self.green}{model}{self.CEND} with variable:{self.green} {var}{self.CEND}')
                value = self._read_csv_funnel(url=path_name)
                my_template = Template(filename=self.temp_chart_file)
                html_chart = my_template.render(values=value,
                                                var=[f'{var}_ref', var],
                                                model=model,
                                                title=f'{model}.mat_{var}')
                with open(f'{self.temp_chart_path}{os.sep}{model}_{var.strip()}.html', "w") as file_tmp:
                    file_tmp.write(html_chart)

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
            my_template = Template(filename=self.temp_chart_file)
            html_chart = my_template.render(values=value_list,
                                            var=legend_list,
                                            model=reference_file,
                                            title=reference_file)
            with open(f'{self.temp_chart_path}{os.sep}{reference_file[reference_file.rfind(os.sep):].replace(".txt", ".html")}', "w") as file_tmp:
                file_tmp.write(html_chart)

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
            my_template = Template(filename=self.temp_chart_file)
            html_chart = my_template.render(values=value,
                                            var=[f'{var}_ref', var],
                                            model=model,
                                            title=f'{model}.mat_{var}')
            with open(f'{self.temp_chart_path}{os.sep}{model}_{var.strip()}.html', "w") as file_tmp:
                file_tmp.write(html_chart)

    def create_index_layout(self):
        """
        Create an index layout from a template
        """
        html_file_list = list()
        for file in os.listdir(self.temp_chart_path):
            if file.endswith(".html") and file != "index.html":
                html_file_list.append(file)
        my_template = Template(filename=self.temp_index_file)
        if len(html_file_list) == 0:
            print(f'No html files')
            os.rmdir(self.temp_chart_path)
            exit(0)
        else:
            html_chart = my_template.render(html_model=html_file_list)
            with open(self.index_html_file, "w") as file_tmp:
                file_tmp.write(html_chart)
            print(f'Create html file with reference results.')

    def create_layout(self, temp_dir: Path, layout_html_file: Path):
        """
        Creates a layout index that has all links to the subordinate index files.
        """
        package_list = list()
        for folders in os.listdir(temp_dir):
            if folders == "style.css" or folders == "index.html":
                continue
            else:
                package_list.append(folders)
        if len(package_list) == 0:
            print(f'No html files')
            exit(0)
        else:
            print(package_list)
            my_template = Template(filename=self.temp_layout_file)
            html_chart = my_template.render(packages=package_list)
            with open(layout_html_file, "w") as file_tmp:
                file_tmp.write(html_chart)

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


class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description='Plot diagramms')
        unit_test_group = parser.add_argument_group("arguments to plot diagrams")
        # [Library - settings]
        unit_test_group.add_argument("--packages",
                                     default="Airflow",
                                     metavar="Modelica.Package",
                                     help="Test only the Modelica package Modelica.Package")
        unit_test_group.add_argument("--library", default="AixLib", help="Library to test")
        # [ bool - flag]
        unit_test_group.add_argument("--line-html-flag",
                                     help='plot a google html chart in line form',
                                     default=True,
                                     action="store_true")
        unit_test_group.add_argument("--error-flag",
                                     default=True,
                                     help='Plot only model with errors',
                                     action="store_true")
        unit_test_group.add_argument("--funnel-comp-flag", default=True,
                                     help="Take the datas from funnel_comp",
                                     action="store_true")
        unit_test_group.add_argument("--create-layout-flag",
                                     default=True,
                                     help='Create a layout with a plots',
                                     action="store_true")
        unit_test_group.add_argument("--line-matplot-flag",
                                     help='plot a matlab chart ',
                                     default=False,
                                     action="store_true")
        unit_test_group.add_argument("--new-ref-flag",
                                     help="Plot new models with new created reference files",
                                     default=False,
                                     action="store_true")
        unit_test_group.add_argument("--show-ref-flag",
                                     help='Plot only model on the interact ci list',
                                     default=False,
                                     action="store_true")
        unit_test_group.add_argument("--update-ref-flag",
                                     help='Plot only updated models',
                                     default=False,
                                     action="store_true")
        unit_test_group.add_argument("--show-package-flag",
                                     help='Plot only updated models',
                                     default=False,
                                     action="store_true")
        unit_test_group.add_argument("--ref-txt-flag",
                                     help="Take the datas from reference datas",
                                     default=False,
                                     action="store_true")
        args = parser.parse_args()
        return args




if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    conf = ci_config()
    check = data_structure()
    check.create_path(conf.chart_dir)
    check.check_path_setting(conf.chart_dir, conf.temp_chart_dir)
    check.check_file_setting(conf.temp_chart_file, conf.temp_index_file,  conf.temp_layout_file)
    charts = Plot_Charts(package=args.packages,
                         library=args.library)
    if args.line_html_flag is True:
        charts.check_setting()
        charts.delete_folder()
        charts.check_folder_path()
        if args.error_flag is True:
            model_var_list = charts.read_unitTest_log()
            print(f'Plot line chart with different reference results.\n')
            for model_variable in model_var_list:
                model_variable = model_variable.split(":")
                if args.funnel_comp_flag is True:
                    charts.mako_line_html_chart(model=model_variable[0],
                                                var=model_variable[1])
                if args.ref_txt_flag is True:
                    ref_file = charts.get_ref_file(model=model_variable[0])
                    if ref_file is None:
                        print(f'Reference file for model {model_variable[0]} does not exist.')
                        continue
                    else:
                        result = charts.get_values(reference_list=ref_file)
                        charts.mako_line_ref_chart(model=model_variable[0],
                                                   var=model_variable[1])
        if args.new_ref_flag is True:
            ref_list = charts.get_new_reference_files()
            charts.write_html_plot_templates(reference_file_list=ref_list)
        if args.update_ref_flag is True:
            ref_list = charts.get_updated_reference_files()
            charts.write_html_plot_templates(reference_file_list=ref_list)
        if args.show_ref_flag is True:
            ref_list = charts.read_show_reference()
            charts.write_html_plot_templates(reference_file_list=ref_list)
        if args.show_package_flag is True:
            folder = charts.get_funnel_comp()
            for ref in folder:
                if args.funnel_comp_flag is True:
                    charts.mako_line_html_chart(model=ref[:ref.find(".mat")],
                                                var=ref[ref.rfind(".mat") + 5:])
        charts.create_index_layout()
        charts.create_layout(temp_dir=Path(conf.chart_dir),
                             layout_html_file=Path(conf.chart_dir,"index.html"))
        check.prepare_data(source_target_dict={conf.chart_dir: Path(conf.result_plot_dir, args.packages)})

    if args.create_layout_flag is True:
        check.create_path(Path(conf.result_plot_dir))
        charts.create_layout(temp_dir=Path(conf.result_plot_dir),
                             layout_html_file=Path(conf.result_plot_dir, "index.html"))

