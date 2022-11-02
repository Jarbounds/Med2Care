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
import configargparse

class MyConfiguration:
    __instance = None

    @staticmethod
    def getInstance() -> object:
        """ Static access method. """
        if MyConfiguration.__instance is None:
            p = configargparse.ArgParser(default_config_files=['../config/config.ini'])

            p.add('-mc', '--my-config', is_config_file=True, help='alternative config file path')

            p.add("-oj", "--path_to_original_json_folder", required=False, help="path to original json", type=str)
            p.add("-ej", "--path_to_entities_json_folder", required=False, help="path to entities json", type=str)
            p.add("-pathcord-ds", "--path_to_cord_ds", required=False, help="path to final csv", type=str)
            p.add("-pathuserid", "--path_to_cord_userid", required=False, help="path to final csv2: user index + author name", type=str)
            p.add("-path_to_cord_all", "--path_to_cord_all", required=False, help="path to final csv2: user index + author name", type=str)

            p.add("-pathmeta", "--path_to_metadata", required=False, help="path to metadata", type=str)
            p.add("-pathblack", "--path_to_blacklist", required=False, help="path to blacklist of articles", type=str)
            p.add("-pathinfo", "--path_to_info", required=False, help="path to metadata of process", type=str)

            p.add("-pathchebi", "--path_chebi", required=False, help="path to chebi ontology", type=str)
            p.add("-pathdo", "--path_do", required=False, help="path to do ontology", type=str)
            p.add("-pathgo", "--path_go", required=False, help="path to go ontology", type=str)
            p.add("-pathhp", "--path_hp", required=False, help="path to hp ontology", type=str)

            p.add("-item1", "--item_prefix1", required=False, help="1st item prefix to load", type=str)
            p.add("-item2", "--item_prefix2", required=False, help="2nd item prefix to load", type=str)
            p.add("-item3", "--item_prefix3", required=False, help="3rd item prefix to load", type=str)
            p.add("-item4", "--item_prefix4", required=False, help="4th item prefix to load", type=str)

            MyConfiguration( p.parse_args() )

        return MyConfiguration.__instance

    def __init__(self, options):

        """
        Virtually private constructor.
        """
        if MyConfiguration.__instance is not None:
            raise Exception( "This class is a singleton!" )
        else:

            self.original_json_folder = options.path_to_original_json_folder
            self.entities_json_folder = options.path_to_entities_json_folder

            self.path_to_cord_ds = options.path_to_cord_ds
            self.path_to_cord_userid = options.path_to_cord_userid
            self.path_to_cord_all = options.path_to_cord_all

            self.path_to_metadata = options.path_to_metadata
            self.path_to_blacklist = options.path_to_blacklist
            self.path_to_info = options.path_to_info

            self.path_chebi = options.path_chebi
            self.path_do = options.path_do
            self.path_go = options.path_go
            self.path_hp = options.path_hp

            self.item_prefix1 = options.item_prefix1
            self.item_prefix2 = options.item_prefix2
            self.item_prefix3 = options.item_prefix3
            self.item_prefix4 = options.item_prefix4

        MyConfiguration.__instance = self