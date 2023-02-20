import argparse
import os
import glob
import shutil
from natsort import natsorted
import sys


class Library_Merge(object):

    def __init__(self, library_dir, merge_library_dir, mos_path, library, merge_library):
        """
        Args:
            library_dir ():
            merge_library_dir ():
            mos_path ():
            library ():
            merge_library ():
        """
        self.library_dir = library_dir
        self.merge_library_dir = merge_library_dir
        self.mos_path = mos_path
        self.library = library
        self.merge_library = merge_library

    def correct_user_guide(self):
        """
        Correct user guide folder
        """
        for root, dirs, files in os.walk(self.library_dir):
            if root[root.rfind(os.sep) + 1:] == "UsersGuide":
                for file in files:
                    if file == "package.order":
                        old_order_file = open(f'{root}{os.sep}{file}', "r")
                        lines = old_order_file.readlines()
                        old_order_file.close()
                        new_order_file = open(f'{root}{os.sep}{file}', "w")
                        for line in lines:
                            if line.strip("\n") != "UsersGuide":
                                new_order_file.write(line)
                        new_order_file.close()

    def _copy_merge_mos_script(self):
        """
    	Copy the Convert_IBPSA_mos Script
    	Returns: return the latest conversion script
    	"""
        if os.path.isdir(self.mos_path):
            pass
        else:
            os.mkdir(self.mos_path)
        mos_file_list = (glob.glob(self.merge_library_dir))
        if len(mos_file_list) == 0:
            print(f'Cant find a Conversion Script in IBPSA Repo')
            exit(0)
        l_ibpsa_conv = natsorted(mos_file_list)[(-1)]
        l_ibpsa_conv = l_ibpsa_conv.replace("/", os.sep)
        l_ibpsa_conv = l_ibpsa_conv.replace("\\", os.sep)
        print(f'Latest IBPSA Conversion script: {l_ibpsa_conv}')
        shutil.copy(l_ibpsa_conv, self.mos_path)
        return l_ibpsa_conv

    def _read_last_library_conversion(self):
        """
    	Read the last aixlib conversion mos script
    	Args:
    	Returns: return the latest library conversion script
    	"""
        filelist = (glob.glob(f'{self.library_dir}{os.sep}*.mos'))
        if len(filelist) == 0:
            print("Cant find a Conversion Script in IBPSA Repo")
            exit(0)
        l_library_conversion = natsorted(filelist)[(-1)]
        l_library_conversion = l_library_conversion.replace("/", os.sep)
        l_library_conversion = l_library_conversion.replace("\\", os.sep)
        print(f'Latest AixLib Conversion script: {l_library_conversion}')
        return l_library_conversion

    def _create_convert_aixlib(self, l_mlibrary_conversion, l_library_conversion):
        """
    	change the paths in the script from IBPSA.Package.model -> AixLib.Package.model
    	Args:
    		l_mlibrary_conversion (): latest merge library conversion script
    		l_library_conversion ():latest library conversion script
    	Returns:
    	    file_new_conv (): file with new conversion script
    	    old_to_numb (): old to number
    	    old_from_numb (): old from number
    	    new_to_numb (): new to number
    	"""
        conversion_number = l_library_conversion[
                            l_library_conversion.find("ConvertAixLib_from_") + 19:l_library_conversion.rfind(".mos")]
        print(f'Latest conversion number: {conversion_number}')  # FROM 1.0.1_TO_1.0.2
        old_from_numb = conversion_number[:conversion_number.find("_to_")]
        old_to_numb = conversion_number[
                      conversion_number.find("_to_") + 4:]  # Update TO Number 1.0.2 old_to_numb == new_from_numb
        first_numb = old_to_numb[:old_to_numb.find(".")]
        sec_numb = int(old_to_numb[old_to_numb.find(".") + 1:old_to_numb.rfind(".")]) + 1
        new_to_numb = f'{first_numb}.{sec_numb}.0'
        new_conv_number = str(old_to_numb) + "_to_" + str(new_to_numb)  # write new conversion number
        file_new_conv = f'{self.mos_path}{os.sep}ConvertAixLib_from_{new_conv_number}.mos'
        mlibrary_file = open(l_mlibrary_conversion, "r")
        library_file = open(file_new_conv, "w+")
        for line in mlibrary_file:
            if line.find(f'Conversion script for {self.merge_library} library') > -1:
                library_file.write(line)
            elif line.find(f'{self.merge_library}') > - 1:
                library_file.write(line.replace(f'{self.merge_library}', f'{self.library}'))
            else:
                library_file.write(line)
        mlibrary_file.close()
        library_file.close()
        return file_new_conv, old_to_numb, old_from_numb, new_to_numb

    def _copy_library_mos(self, file_new_conversion):
        """
    	Args:
    		file_new_conversion (): copy the new conversion file to library script folder
    	Returns:
    	    new_conversion_script (): return the new conversion script path
    	"""
        new_conversion_script = shutil.copy(file_new_conversion, self.library_dir)
        shutil.rmtree(self.mos_path)
        return new_conversion_script

    def _compare_conversion(self, l_mlibrary_conversion, l_library_conversion):
        """
        Compare the latest library conversion script with the latest merge library conversion script
    	Args:
    		l_mlibrary_conversion (): latest merge library conversion script
    		l_library_conversion (): latest library conversion script
    	Returns:
    	    False (): Boolean argument: True - Conversion script is up-to-date , False Conversion script is not up-to-date
    	"""
        result = True
        with open(l_mlibrary_conversion) as file_1:
            file_1_text = file_1.readlines()
        with open(l_library_conversion) as file_2:
            file_2_text = file_2.readlines()
        for line1, line2 in zip(file_1_text, file_2_text):
            if line1 == line2.replace(f'{self.library}', f'{self.merge_library}'):
                continue
            else:
                result = False
        return result

    def _add_conv_to_package(self, l_library_conv, new_conversion_script, old_to_numb, new_to_numb):
        """
        write the new conversion script in the package.mo of the library
    	Args:
    		l_library_conv (): latest library conversion script
    		new_conversion_script (): new library conversion script
    		old_to_numb (): old to number
    		new_to_numb (): new to number
    	"""
        l_library_conv = l_library_conv.replace('\\', '/')
        new_conversion_script = new_conversion_script.replace('\\', '/')
        file = open(f'AixLib{os.sep}package.mo', "r")
        version_list = []
        for line in file:
            if line.find("version") == 0 or line.find('script="modelica://') == 0:
                version_list.append(line)
                continue
            if line.find(f'  version = "{old_to_numb}",') > -1:
                version_list.append(line.replace(old_to_numb, new_to_numb))
                continue
            if line.find(f'{l_library_conv}') > -1:
                version_list.append(line.replace(")),", ","))
                version_list.append(f'    version="{old_to_numb}",\n')
                version_list.append(f'                      script="modelica://{new_conversion_script}")),\n')
                continue
            else:
                version_list.append(line)
                continue
        file.close()
        pack = open(f'{self.library}{os.sep}package.mo', "w")
        for version in version_list:
            pack.write(version)
        pack.close()

    def merge_workflow(self):
        """

        """
        last_mlibrary_conversion = self._copy_merge_mos_script()
        last_library_conversion = self._read_last_library_conversion()
        result = self._compare_conversion(l_mlibrary_conversion=last_mlibrary_conversion,
                                          l_library_conversion=last_library_conversion)
        if result is True:
            print(
                f'The latest {self.library} conversion script {last_library_conversion} is up to date with {self.merge_library} conversion script {last_mlibrary_conversion}')
        else:
            conv_data = self._create_convert_aixlib(l_mlibrary_conversion=last_mlibrary_conversion,
                                                    l_library_conversion=last_library_conversion)
            if conv_data[0] is None:
                print(f'please check when the last merge took place')
                shutil.rmtree(args.dst)
            else:
                new_conversion_script = self._copy_library_mos(file_new_conversion=conv_data[0])
                self._add_conv_to_package(l_library_conv=last_library_conversion,
                                          new_conversion_script=new_conversion_script,
                                          old_to_numb=conv_data[1],
                                          new_to_numb=conv_data[3])
                print(f'New {self.library} Conversion scrip was created: {conv_data[0]}')


class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description="Variables to start a library merge")
        check_test_group = parser.add_argument_group("Arguments to set environment variables")
        check_test_group.add_argument("--library-dir",
                                      default="AixLib\\Resources\\Scripts",
                                      help="path to the library scripts")
        check_test_group.add_argument("--merge-library-dir",
                                      default='modelica-ibpsa\\IBPSA\\Resources\\Scripts\\Dymola\\ConvertIBPSA_*',
                                      help="path to the merge library scripts")
        check_test_group.add_argument("--mos-path",
                                      default="Convertmos",
                                      help="Folder where the conversion scripts are stored temporarily")
        check_test_group.add_argument("--library",
                                      default="AixLib",
                                      help="Library to be merged into")
        check_test_group.add_argument("--merge-library",
                                      default='IBPSA',
                                      help="Library to be merged")
        args = parser.parse_args()
        return args


if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    merge = Library_Merge(library_dir=args.library_dir,
                          merge_library_dir=args.merge_library_dir,
                          mos_path=args.mos_path,
                          library=args.library,
                          merge_library=args.merge_library)
    merge.merge_workflow()
    merge.correct_user_guide()
