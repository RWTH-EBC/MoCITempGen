from Dymola_python_tests.CI_test_config import CI_config



class data_strucutre(CI_config):

    def __init__(self):
        super().__init__()


# *********** Checking structure *******************
    def check_arguments_settings(self, *args):
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'***--- Argument setting---****')
        for i, (var, val) in enumerate(zip(var_names, args)):
            if val is None:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}Variable "{var}"{self.CEND} has value {self.CRED}"{val}". "{var}"{self.CEND} is not set!')
                print(f'***------****')
                exit(1)
            else:
                print(f'{self.green}Setting:{self.CEND} {self.blue}Variable "{var}" {self.CEND} is set as: {self.blue}"{val}"{self.CEND}')
        print(f'***------****')

    def check_path_setting(self, *args: str):
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'***--- Check path setting---****')
        for i, (var, path) in enumerate(zip(var_names, args)):
            if os.path.isdir(path) is True:
                print(f'{self.green}Setting:{self.CEND} {self.blue}Path_variable "{var}"{self.CEND} is set as: {self.blue}"{path}"{self.CEND} and exists.')
            else:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}Path_variable "{var}"{self.CEND} in {self.blue}"{path}"{self.CEND} does not exist.')
                print(f'***------****')
                exit(1)
        print(f'***------****')

    def check_file_setting(self, *args):
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'***--- Check file setting---****')
        for i, (var, file) in enumerate(zip(var_names, args)):
            if os.path.isfile(file) is True:
                print(f'{self.green}Setting:{self.CEND} {self.blue}File "{var}"{self.CEND} is set as: {self.blue}"{file}"{self.CEND} and exists.')
            else:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}File_variable "{var}"{self.CEND} in {self.blue}"{file}"{self.CEND} does not exist.')
                print(f'***------****')
                exit(1)
        print(f'***------****')

    ############# Create Structure ##############
    def create_path(self, path_list: list = None):
        if path_list is not None:
            print(f'\n**** Create folder ****\n')
            for path in path_list:
                print(f'{self.green}Create Folder:{self.CEND} {path}')
                os.makedirs(path, exist_ok=True)
            print(f'\n**** ----------- ****\n')

    def create_files(self, files_list: list = None):
        """
        Args:
            files_list ():
        """
        if folder_list is not None:
            print(f'\n**** Create file structure ****\n')
            for file in files_list:
                if os.path.exists(file):
                    print(f'{file} does exist.')
                else:
                    print(f'File {file} does not exist. Create a new one under {self.green}{file}{self.CEND}')
                    write_file = open(file, "w+")
                    if file is self.config_ci_eof_file:
                        write_file.write(f'y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
                    write_file.close()
            print(f'\n**********************\n')



    ############# Remove Structure ##############
    def delete_files_in_path(self, path_list: list = None):
        if path_list is not None:
            print(f'\n**** Delete folder ****\n')
            for path in path_list:
                print(f'{self.green}Delete files:{self.CEND} {path}')
                for filename in os.listdir(path):
                    file_path = os.path.join(path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
            print(f'\n**** ----------- ****\n')

    def delete_spec_file(self, root: str = None, pattern: str = None):
        if root is not None and pattern is not None:
            for filename in os.listdir(root):
                file = os.path.join(root, filename)
                if os.path.isfile(file) and filename.find(pattern) > -1:
                    os.remove(file)

    @staticmethod
    def remove_files(file_list: list = None):
        if file_list is not None:
            for file in file_list:
                if os.path.exists(file):
                    if os.path.isfile(file) is True:
                        os.remove(file)
                        print(f'Remove file: {file}')
                    else:
                        print(f'File {file} does not exist')


    def remove_path(self, path_list: list = None):
        if path_list is not None:
            for path in path_list:
                if os.path.isdir(path) is True:
                    os.rmdir(path)
                    print(f'Remove folder: {path}')
                else:
                    print(f'Path {path} does not exist.')

    ############# Prepare Result ##############

    def prepare_data(self,
                     source_target_dict: dict = None,
                     del_flag: bool = False):
        """
            Args:
            file_path_dict (): {dst:src,}
            del_flag (): True: delete file, False dont delete file
        """
        print(f'\n{self.blue}**** Prepare Data ****{self.CEND}')
        if source_target_dict is not None:
            for source in source_target_dict:
                target_path = source_target_dict[source]
                if not os.path.exists(target_path):
                    print(f'Create path: {target_path}')
                    os.makedirs(target_path)
                if os.path.isfile(source) is True:
                    path, file_name = os.path.split(source)
                    target = os.path.join(target_path, file_name)
                    print(f'Result file {self.blue}{source}{self.CEND} was moved to {self.blue}{target}{self.CEND}')
                    shutil.copyfile(source, target)
                    if del_flag is True:
                        self.remove_files([source])
                if os.path.isdir(source) is True:
                    print(f'Result Folder {self.blue}{source}{self.CEND} was moved to {self.blue}{target_path}{self.CEND}')
                    shutil.copytree(source, target_path)
                    if del_flag is True:
                        self.remove_path([source])
        print(f'{self.blue}**********************{self.CEND}\n')


    # *******************************
    @staticmethod
    def return_file_list():
        """
        Returns:
        """
        files_list = []
        file_dic = (vars(CI_config()))
        for file in file_dic:
            if file.find("_file") > -1:
                files_list.append(file_dic[file])
        return files_list

    @staticmethod
    def return_file_dir():
        dir_list = []
        dir_dic = (vars(CI_config()))
        for dirs in dir_dic:
            if dirs.find("_dir") > -1:
                dir_list.append(dir_dic[dirs])
        return dir_list