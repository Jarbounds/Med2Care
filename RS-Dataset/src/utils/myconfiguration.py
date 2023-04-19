###############################################################################
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License"); you may     #
# not use this file except in compliance with the License. You may obtain a   #
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0           #
#                                                                             #
# Unless required by applicable law or agreed to in writing, software         #
# distributed under the License is distributed on an "AS IS" BASIS,           #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions and         #
# limitations under the License.                                              #
#                                                                             #
###############################################################################
#                                                                             #  
# @author Matilde Pato                                                        #  
# @email: matilde.pato@gmail.pt                                               #
# @date: March, 26th 2021                                                     #
# @version: 1.0                                                               #  
# @last update:                                                               #   
#                                                                             #  
#                                                                             #  
###############################################################################
# 
from configargparse import ArgParser


class MyConfiguration:
    __instance = None

    @staticmethod
    def get_instance() -> 'MyConfiguration':
        """ Static access method. """
        if MyConfiguration.__instance is None:
            p: ArgParser = ArgParser(default_config_files=['../configurations/configurations.ini'])

            p.add(
                "-author_names",
                "--author_names",
                required=False,
                help='Author names'
            )
            p.add(
                "-mc",
                "--my-configurations",
                is_config_file=True,
                help='alternative configurations file path'
            )
            p.add(
                "-oj",
                "--path_to_original_json_folder",
                required=False,
                help="path to original json",
                type=str
            )
            p.add(
                "-ej",
                "--path_to_entities_json_folder",
                required=False,
                help="path to entities json",
                type=str
            )
            p.add(
                "-path_ds",
                "--path_ds",
                required=False,
                help="path to final csv",
                type=str
            )
            p.add(
                "-pathmeta",
                "--path_to_metadata",
                required=False,
                help="path to metadata",
                type=str)
            p.add(
                "-pathblack",
                "--path_to_blacklist",
                required=False,
                help="path to blacklist of articles",
                type=str
            )
            p.add(
                "-pathinfo",
                "--path_to_info",
                required=False,
                help="path to metadata of process",
                type=str
            )
            p.add(
                "-pathchebi",
                "--path_chebi",
                required=False,
                help="path to chebi ontology",
                type=str
            )
            p.add(
                "-pathdo",
                "--path_do",
                required=False,
                help="path to do ontology",
                type=str
            )
            p.add(
                "-item1",
                "--item_prefix1",
                required=False,
                help="1st item prefix to load",
                type=str
            )
            p.add(
                "-item2",
                "--item_prefix2",
                required=False,
                help="2nd item prefix to load",
                type=str
            )
            p.add(
                "-path_kb",
                "--path_kb",
                required=False,
                help="Path to the Knowledge Graph (KB) step",
                type=str
            )
            p.add(
                "-path_algorithm",
                "--path_algorithms",
                required=False,
                help="Path to recommender system algorithms",
                type=str
            )
            p.add(
                "-transfer_option",
                "--transfer_option",
                required=False,
                help="Transfer option to perform (copy or move)",
                type=str
            )
            p.add(
                "-ds_name",
                "--ds_name",
                required=False,
                help="Resultant dataset name",
                type=str
            )

            MyConfiguration(p.parse_args())

        return MyConfiguration.__instance

    def __init__(self, options):

        """
        Virtually private constructor.
        """
        if MyConfiguration.__instance is not None:
            raise Exception("This class is a singleton!")
        else:

            self.original_json_folder = options.path_to_original_json_folder
            self.entities_json_folder = options.path_to_entities_json_folder

            self.path_ds = options.path_ds

            self.path_to_metadata = options.path_to_metadata
            self.path_to_blacklist = options.path_to_blacklist
            self.path_to_info = options.path_to_info

            self.path_chebi = options.path_chebi
            self.path_do = options.path_do

            self.item_prefix1 = options.item_prefix1
            self.item_prefix2 = options.item_prefix2

            self.item_prefix = f'{self.item_prefix1},{self.item_prefix2}'

            self.path_kb = options.path_kb
            self.path_algorithms = options.path_algorithms

            self.ds_name = options.ds_name

            self.transfer_option = options.transfer_option

        MyConfiguration.__instance = self
